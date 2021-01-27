from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .table import FetchDate, Config
import pandas as pd

# No more pop, pop target, Indicator


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    """
    Singleton database class
    ! This class should be called for the first time with DB bind_string.

    Keyword arguments:
    bind_string -- SQLAlchemy-like DB bind string
    Return: Database
    """

    fetch_data_query = """SELECT * FROM {}"""

    # TODO have thislinked to DEFAULT

    active_repo = "out"

    data_types = {
        "district_name": str,
        "facility_name": str,
        "date": "datetime64[ns]",
        "indicator_name": str,
        "*": int,
    }

    index_columns = ["id", "facility_name", "date"]

    pop_markers = ["coverage", "(per "]

    datasets = {}
    raw_data = None
    rep_data = None

    init = False

    def __init__(self, bind_string=None):  # From here
        if bind_string:
            # Set SQLAlchemy
            self.engine = create_engine(bind_string)
            self.Session = sessionmaker(bind=self.engine)
            self.init = True
            # Get the supporting data
            self.set_indicator_groups_and_view()
            # Get init data
            self.raw_data = self.get_repository(self.active_repo)
            self.rep_data = self.get_repository("rep")
            self.set_districts()

        assert self.init, "You must pass a DB bind string to use Database first!"

    @property
    def indicator_dropdowns(self):
        return self.__indicator_dropdowns

    # Initialization methods
    def set_districts(self):
        self.districts = self.raw_data.id.unique()
        self.districts.sort()

    def set_indicator_groups_and_view(self):
        serialized_groups = self.get_serialized_obj(Config)
        self.__indicator_serialized = serialized_groups
        indicator_groups = pd.DataFrame(serialized_groups)
        self.__indicator_dropdowns = (
            indicator_groups[["config_group", "config_indicator"]]
            .copy()
            .reset_index(drop=True)
        )

    # Fetching data, DB adapter
    def get_repository(self, repo_name):
        print(f"Fetching data from {repo_name}")

        __dataframe = pd.read_sql(
            self.fetch_data_query.format(repo_name), con=self.engine
        )

        __dataframe["date"] = __dataframe["date"].astype("datetime64[ns]")

        __dataframe.rename(columns={"district_name": "id"}, inplace=True)

        return __dataframe

    def get_serialized_into_df(self, sqlalchemy_obj):
        df = pd.DataFrame(self.get_serialized_obj(sqlalchemy_obj))
        return df

    @property
    def fetch_date(self):
        session = self.Session()
        date = session.query(FetchDate).one()
        session.close()
        return date.serialize()

    def get_serialized_obj(self, sqlalchemy_obj):
        session = self.Session()
        objects = session.query(sqlalchemy_obj).all()
        serialized = [obj.serialize() for obj in objects]
        session.close()
        return serialized

    # Active raw data management
    def filter_by_policy(self, policy):
        dropdown_filters = {
            "Correct outliers - using standard deviation": "std",
            "Correct outliers - using interquartile range": "iqr",
            "Keep outliers": "out",
        }
        new_repo = dropdown_filters.get(policy)
        if self.active_repo == new_repo:
            return self.raw_data
        self.active_repo = new_repo
        self.raw_data = None
        self.raw_data = self.get_repository(self.active_repo)
        return self.raw_data

    # Active dataset management
    def include_dataset(self, key, df):
        self.datasets[key] = df

    def fetch_dataset(self, key):
        return self.datasets.get(key)

    # Data filters

    def get_is_ratio(self, indicator):
        ratio_list = [
            x.get("config_indicator")
            for x in self.__indicator_serialized
            if x.get("config_function") == "ratio"
        ]
        return indicator in ratio_list

    def filter_by_indicator(self, df, indicator):

        config = self.get_serialized_into_df(Config)

        function = config[config.config_indicator == indicator][
            "config_function"
        ].values[0]

        is_ratio = function == "ratio"

        if is_ratio == False:
            try:
                df = df[list(self.index_columns) + [indicator]]
            except Exception as e:
                print(e)
                print("No such column is present in the dataframe")

        else:

            nominator = f"{indicator}__wr"

            denominator = config[config.config_indicator == indicator][
                "config_denominator"
            ].values[0]
            denominator = f"{denominator}__w"

            try:
                df = df[list(self.index_columns) + [nominator, denominator]]
            except Exception as e:
                print(e)
                print("No such columns are present in the dataframe")

        return df

    def switch_indic_to_numerator(self, indicator, popcheck=True):

        if popcheck:
            needs_switch = any(map(indicator.__contains__, self.pop_markers))

        else:
            config = self.get_serialized_into_df(Config)
            function = config[config.config_indicator == indicator][
                "config_function"
            ].values[0]
            needs_switch = function == "ratio"

        if needs_switch:
            new_indic = indicator.split(" (")[0]
            return new_indic

        else:

            return indicator

    # Labels

    def get_renaming_dict(
        self,
        rename_from="config_indicator",
        rename_to="config_view",
    ):
        return {
            x.get(rename_from): x.get(rename_to) for x in self.__indicator_serialized
        }

    # TODO : Understand the need for if statement below

    def get_indicator_view(
        self, indicator, rename_from="indicator", rename_to="view", indicator_group=None
    ):
        if indicator_group:
            for x in self.__indicator_serialized:
                if (
                    x.get("config_group") == indicator_group
                    and x.get(f"config_{rename_from}") == indicator
                ):
                    return x.get(f"config_{rename_to}")
        else:
            return self.get_renaming_dict(
                rename_from=f"config_{rename_from}",
                rename_to=f"config_{rename_to}",
            ).get(indicator)

    def init_pipeline(self, functions):
        # {"dataset_name": {"function": func, "args": args}}
        self.pipeline = functions

    def run_pipeline(self, controls):
        for dataset_name, function in self.pipeline.items():
            self.include_dataset(dataset_name, function(self, **controls))
