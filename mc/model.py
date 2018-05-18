import csv
import enum
import datetime
import typing
from mc import db
import mc.mc_global


class MoveDirectionEnum(enum.Enum):
    up = 1
    down = 2


class MinOrMaxEnum(enum.Enum):
    min = "MIN"
    max = "MAX"


def db_exec(i_sql: str, i_params: tuple=None):
    db_connection = db.Helper.get_db_connection()
    db_cursor = db_connection.cursor()
    # noinspection PyUnusedLocal
    db_cursor_result = None
    if i_params is not None:
        db_cursor_result = db_cursor.execute(i_sql, i_params)
    else:
        db_cursor_result = db_cursor.execute(i_sql)
    db_connection.commit()
    return db_cursor_result


class PhrasesM:
    def __init__(
        self,
        i_id: int,
        i_vert_order: int,
        i_title: str,
        i_ib: str,
        i_ob: str,
        i_ib_short: str,
        i_ob_short: str,
        i_type: int
    ) -> None:
        self._id_int = i_id
        self._vert_order_int = i_vert_order
        self._title_str = i_title
        self._ib_str = i_ib
        self._ob_str = i_ob
        self._ib_short_str = i_ib_short
        self._ob_short_str = i_ob_short
        self._type_enum = mc.mc_global.BreathingPhraseType.in_out
        if i_type == mc.mc_global.BreathingPhraseType.single.value:
            self._type_enum = mc.mc_global.BreathingPhraseType.single

    @property
    def id(self) -> int:
        return self._id_int

    @property
    def title(self) -> str:
        return self._title_str

    @title.setter
    def title(self, i_new_title: str) -> None:
        self._title_str = i_new_title
        self._update_obj(db.Schema.PhrasesTable.Cols.title, i_new_title)

    @property
    def vert_order(self) -> int:
        return self._vert_order_int

    @vert_order.setter
    def vert_order(self, i_new_vert_order: int) -> None:
        self._vert_order_int = i_new_vert_order
        self._update_obj(db.Schema.PhrasesTable.Cols.vertical_order, i_new_vert_order)

    @property
    def ib(self) -> str:
        return self._ib_str

    @ib.setter
    def ib(self, i_new_ib: str) -> None:
        self._ib_str = i_new_ib
        self._update_obj(db.Schema.PhrasesTable.Cols.ib_phrase, i_new_ib)

    @property
    def ob(self) -> str:
        return self._ob_str

    @ob.setter
    def ob(self, i_new_ob: str) -> None:
        self._ib_str = i_new_ob
        self._update_obj(db.Schema.PhrasesTable.Cols.ob_phrase, i_new_ob)

    @property
    def ib_short(self) -> str:
        return self._ib_short_str

    @ib_short.setter
    def ib_short(self, i_new_ib_short: str) -> None:
        self._ib_short_str = i_new_ib_short
        self._update_obj(db.Schema.PhrasesTable.Cols.ib_short_phrase, i_new_ib_short)

    @property
    def ob_short(self) -> str:
        return self._ob_short_str

    @ob_short.setter
    def ob_short(self, i_new_ob_short: str) -> None:
        self._ob_short_str = i_new_ob_short
        self._update_obj(db.Schema.PhrasesTable.Cols.ob_short_phrase, i_new_ob_short)

    @property
    def type(self) -> mc.mc_global.BreathingPhraseType:
        return self._type_enum

    @type.setter
    def type(self, i_new_type: mc.mc_global.BreathingPhraseType) -> None:
        self._type_enum = i_new_type
        self._update_obj(db.Schema.PhrasesTable.Cols.type, i_new_type.value)

    """
    def _update_obj(self, i_col_name: str, i_new_value) -> None:
        db_exec(
            "UPDATE " + db.Schema.PhrasesTable.name
            + " SET " + i_col_name + " = ?"
            + " WHERE " + db.Schema.PhrasesTable.Cols.id + " = ?",
            (i_new_value, str(self._id_int))
        )
    """

    def _update_obj(self, i_col_name: str, i_new_value) -> None:
        PhrasesM._update(self._id_int, i_col_name, i_new_value)

    @staticmethod
    def _update(i_id: int, i_col_name: str, i_new_value):
        db_exec(
            "UPDATE " + db.Schema.PhrasesTable.name
            + " SET " + i_col_name + " = ?"
            + " WHERE " + db.Schema.PhrasesTable.Cols.id + " = ?",
            (i_new_value, str(i_id))
        )

    @staticmethod
    def add(i_title: str, i_ib: str, i_ob: str, ib_short: str, ob_short: str,
    i_type: mc.mc_global.BreathingPhraseType) -> None:
        vertical_order_last_pos_int = PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)
        # -this is the last pos before the new entry has been added, therefore + 1 is added below
        db_exec(
            "INSERT INTO " + db.Schema.PhrasesTable.name + "("
            + db.Schema.PhrasesTable.Cols.vertical_order + ", "
            + db.Schema.PhrasesTable.Cols.title + ", "
            + db.Schema.PhrasesTable.Cols.ib_phrase + ", "
            + db.Schema.PhrasesTable.Cols.ob_phrase + ", "
            + db.Schema.PhrasesTable.Cols.ib_short_phrase + ", "
            + db.Schema.PhrasesTable.Cols.ob_short_phrase + ", "
            + db.Schema.PhrasesTable.Cols.type
            + ") VALUES (?, ?, ?, ?, ?, ?, ?)",
            (vertical_order_last_pos_int + 1, i_title, i_ib, i_ob, ib_short, ob_short, i_type.value)
        )

    @staticmethod
    def get(i_id: int):  # -cannot write type PhrasesM here, unknown why
        db_cursor_result = db_exec(
            "SELECT * FROM " + db.Schema.PhrasesTable.name
            + " WHERE " + db.Schema.PhrasesTable.Cols.id + "=?",
            (str(i_id),)
        )
        reminder_db_te = db_cursor_result.fetchone()
        return PhrasesM(*reminder_db_te)
        # -the asterisk (*) will "expand" the tuple into separate arguments for the function header

    @staticmethod
    def get_all() -> list:
        ret_phrase_list = []
        db_cursor_result = db_exec(
            "SELECT * FROM " + db.Schema.PhrasesTable.name
            + " ORDER BY " + db.Schema.PhrasesTable.Cols.vertical_order
        )
        phrases_db_te_list = db_cursor_result.fetchall()
        for phrases_db_te in phrases_db_te_list:
            ret_phrase_list.append(PhrasesM(*phrases_db_te))
        return ret_phrase_list

    @staticmethod
    def remove(i_id: int) -> None:
        db_exec(
            "DELETE FROM " + db.Schema.PhrasesTable.name
            + " WHERE " + db.Schema.PhrasesTable.Cols.id + "=?",
            (str(i_id),)
        )

    @staticmethod
    def is_empty() -> bool:
        db_cursor_result = db_exec(
            "SELECT count(*) FROM "
            + db.Schema.PhrasesTable.name
        )
        empty_rows_te = db_cursor_result.fetchone()
        # logging.debug("*empty_rows_te = " + str(*empty_rows_te))
        if empty_rows_te[0] == 0:
            return True
        else:
            return False

    """
    @staticmethod
    def update_sort_order(i_id: int, i_move_direction: MoveDirectionEnum) -> bool:
        if i_id == mc.mc_global.NO_PHRASE_SELECTED_INT:
            return False
        main_id_int = i_id
        main_sort_order_int = PhrasesM.get(i_id)._vert_order_int
        if i_move_direction == MoveDirectionEnum.up:
            if (main_sort_order_int <= PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.min)
            or main_sort_order_int > PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)):
                return False
        elif i_move_direction == MoveDirectionEnum.down:
            if (main_sort_order_int < PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.min)
            or main_sort_order_int >= PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)):
                return False
        other = PhrasesM._get_by_vert_order(main_sort_order_int, i_move_direction)
        other_id_int = other._id_int
        other_sort_order_int = other._vert_order_int

        PhrasesM._update(main_id_int, db.Schema.PhrasesTable.Cols.vertical_order, other_sort_order_int)
        PhrasesM._update(other_id_int, db.Schema.PhrasesTable.Cols.vertical_order, main_sort_order_int)

        ########TODO: problem here, mo0ving in the other direction?!


        return True
    """

    @staticmethod
    def update_sort_order(i_id: int, i_sort_order: int) -> None:
        PhrasesM._update(i_id, db.Schema.PhrasesTable.Cols.vertical_order, i_sort_order)

    @staticmethod
    def update_sort_order_move_up_down(i_id: int, i_move_direction: MoveDirectionEnum) -> bool:
        if i_id == mc.mc_global.NO_PHRASE_SELECTED_INT:
            return False
        main_id_int = i_id
        main_sort_order_int = PhrasesM.get(i_id)._vert_order_int
        if i_move_direction == MoveDirectionEnum.up:
            if (main_sort_order_int <= PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.min)
            or main_sort_order_int > PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)):
                return False
        elif i_move_direction == MoveDirectionEnum.down:
            if (main_sort_order_int < PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.min)
            or main_sort_order_int >= PhrasesM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)):
                return False
        other = PhrasesM._get_by_vert_order(main_sort_order_int, i_move_direction)
        other_id_int = other._id_int
        other_sort_order_int = other._vert_order_int

        PhrasesM._update(main_id_int, db.Schema.PhrasesTable.Cols.vertical_order, other_sort_order_int)
        PhrasesM._update(other_id_int, db.Schema.PhrasesTable.Cols.vertical_order, main_sort_order_int)

        return True

    @staticmethod
    def _get_by_vert_order(i_sort_order: int, i_move_direction: MoveDirectionEnum):
        direction_as_lt_gt_str = ">"
        sort_direction_str = "DESC"
        if i_move_direction == MoveDirectionEnum.up:
            direction_as_lt_gt_str = "<"
            sort_direction_str = "DESC"
        elif i_move_direction == MoveDirectionEnum.down:
            direction_as_lt_gt_str = ">"
            sort_direction_str = "ASC"

        db_cursor_result = db_exec(
            "SELECT * FROM " + db.Schema.PhrasesTable.name
            + " WHERE " + db.Schema.PhrasesTable.Cols.vertical_order + direction_as_lt_gt_str + str(i_sort_order)
            + " ORDER BY " + db.Schema.PhrasesTable.Cols.vertical_order + " " + sort_direction_str
        )
        phrase_db_te = db_cursor_result.fetchone()

        return PhrasesM(*phrase_db_te)

    @staticmethod
    def _get_highest_or_lowest_sort_value(i_min_or_max: MinOrMaxEnum) -> int:
        db_cursor_result = db_exec(
            "SELECT " + i_min_or_max.value
            + " (" + mc.db.Schema.PhrasesTable.Cols.vertical_order + ")"
            + " FROM " + mc.db.Schema.PhrasesTable.name
        )
        return_value_int = db_cursor_result.fetchone()[0]
        # -0 has to be added here even though there can only be one value

        if return_value_int is None:
            # -to prevent error when the tables are empty
            return 0
        return return_value_int


class RestActionsM:
    def __init__(
        self,
        i_id: int,
        i_vertical_order: int,
        i_title: str
    ) -> None:
        self._id_int = i_id
        self._vert_order_int = i_vertical_order
        self._title_str = i_title

    @property
    def id(self) -> int:
        return self._id_int
    # no setter

    @property
    def vert_order(self) -> int:
        return self._vert_order_int
    # no setter

    @property
    def title(self) -> str:
        return self._title_str

    @title.setter
    def title(self, i_new_title: str) -> None:
        self._title_str = i_new_title
        self._update_obj(db.Schema.RestActionsTable.Cols.title, i_new_title)

    def _update_obj(self, i_col_name: str, i_new_value) -> None:
        RestActionsM._update(self._id_int, i_col_name, i_new_value)

    @staticmethod
    def _update(i_id: int, i_col_name: str, i_new_value):
        db_exec(
            "UPDATE " + db.Schema.RestActionsTable.name
            + " SET " + i_col_name + " = ?"
            + " WHERE " + db.Schema.RestActionsTable.Cols.id + " = ?",
            (i_new_value, str(i_id))
        )

    @staticmethod
    def add(i_title: str) -> None:
        vertical_order_last_pos_int = RestActionsM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)
        # -this is the last pos before the new entry has been added, therefore + 1 is added below
        db_exec(
            "INSERT INTO " + db.Schema.RestActionsTable.name + "("
            + db.Schema.RestActionsTable.Cols.vertical_order + ", "
            + db.Schema.RestActionsTable.Cols.title
            + ") VALUES (?, ?)",
            (vertical_order_last_pos_int + 1, i_title)
        )

    @staticmethod
    def get(i_id: int):
        db_cursor_result = db_exec(
            "SELECT * FROM " + db.Schema.RestActionsTable.name
            + " WHERE " + db.Schema.RestActionsTable.Cols.id + "=?",
            (str(i_id),)
        )
        rest_action_db_te = db_cursor_result.fetchone()
        return RestActionsM(*rest_action_db_te)
        # -the asterisk (*) will "expand" the tuple into separate arguments for the function header

    @staticmethod
    def remove(i_id: int) -> None:
        db_exec(
            "DELETE FROM " + db.Schema.RestActionsTable.name
            + " WHERE " + db.Schema.RestActionsTable.Cols.id + "=?",
            (str(i_id),)
        )

    @staticmethod
    def get_all() -> list:
        ret_reminder_list = []
        db_cursor_result = db_exec(
            "SELECT * FROM " + db.Schema.RestActionsTable.name
            + " ORDER BY " + db.Schema.RestActionsTable.Cols.vertical_order
        )
        rest_actions_db_te_list = db_cursor_result.fetchall()
        for rest_action_db_te in rest_actions_db_te_list:
            ret_reminder_list.append(RestActionsM(*rest_action_db_te))
        return ret_reminder_list

    @staticmethod
    def update_sort_order_move_up_down(i_id: int, i_move_direction: MoveDirectionEnum) -> bool:
        if i_id == mc.mc_global.NO_REST_ACTION_SELECTED_INT:
            return False
        main_id_int = i_id
        main_sort_order_int = RestActionsM.get(i_id)._vert_order_int
        if i_move_direction == MoveDirectionEnum.up:
            if (main_sort_order_int <= RestActionsM._get_highest_or_lowest_sort_value(MinOrMaxEnum.min)
            or main_sort_order_int > RestActionsM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)):
                return False
        elif i_move_direction == MoveDirectionEnum.down:
            if (main_sort_order_int < RestActionsM._get_highest_or_lowest_sort_value(MinOrMaxEnum.min)
            or main_sort_order_int >= RestActionsM._get_highest_or_lowest_sort_value(MinOrMaxEnum.max)):
                return False
        other = RestActionsM.get_by_vert_order(main_sort_order_int, i_move_direction)
        other_id_int = other.id
        other_sort_order_int = other._vert_order_int

        RestActionsM._update(main_id_int, db.Schema.RestActionsTable.Cols.vertical_order, other_sort_order_int)
        RestActionsM._update(other_id_int, db.Schema.RestActionsTable.Cols.vertical_order, main_sort_order_int)

        return True

    @staticmethod
    def get_by_vert_order(i_sort_order: int, i_move_direction: MoveDirectionEnum):
        direction_as_lt_gt_str = ">"
        sort_direction_str = "DESC"
        if i_move_direction == MoveDirectionEnum.up:
            direction_as_lt_gt_str = "<"
            sort_direction_str = "DESC"
        elif i_move_direction == MoveDirectionEnum.down:
            direction_as_lt_gt_str = ">"
            sort_direction_str = "ASC"
        db_cursor_result = db_exec(
            "SELECT * FROM " + db.Schema.RestActionsTable.name
            + " WHERE " + db.Schema.RestActionsTable.Cols.vertical_order
            + " " + direction_as_lt_gt_str + " " + str(i_sort_order)
            + " ORDER BY " + db.Schema.RestActionsTable.Cols.vertical_order + " " + sort_direction_str
        )
        journal_db_te = db_cursor_result.fetchone()
        return RestActionsM(*journal_db_te)

    @staticmethod
    def _get_highest_or_lowest_sort_value(i_min_or_max: MinOrMaxEnum) -> int:
        db_cursor_result = db_exec(
            "SELECT " + i_min_or_max.value
            + " (" + mc.db.Schema.RestActionsTable.Cols.vertical_order + ")"
            + " FROM " + mc.db.Schema.RestActionsTable.name
        )
        return_value_int = db_cursor_result.fetchone()[0]
        # -0 has to be added here even though there can only be one value

        if return_value_int is None:
            # -to prevent error when the tables are empty
            return 0
        return return_value_int


class SettingsM:
    # noinspection PyUnusedLocal
    def __init__(
        self,
        i_id: int,  # unused
        i_rest_reminder_active: int,
        i_rest_reminder_interval: int,
        i_rest_reminder_audio_filename: str,
        i_rest_reminder_volume: int,
        i_rest_reminder_notification_type: int,
        i_breathing_reminder_active: int,
        i_breathing_reminder_interval: int,
        i_breathing_reminder_audio_filename: str,
        i_breathing_reminder_audio_volume: int,
        i_breathing_reminder_notification_type: int,
        i_breathing_reminder_phrase_setup: int,
        i_breathing_reminder_nr_before_dialog: int,
        i_breathing_reminder_dialog_audio_active: int,
        i_breathing_reminder_dialog_close_on_active: int,
        i_breathing_reminder_text: str,
        i_breathing_dialog_phrase_selection: int,
        i_prep_reminder_audio_filename: str,
        i_prep_reminder_audio_volume: int,
        i_run_on_startup: int,
        i_nr_times_started_since_last_feedback_notif: int
    ) -> None:
        self.rest_reminder_active_bool = True if i_rest_reminder_active else False
        self.rest_reminder_interval_int = i_rest_reminder_interval
        self.rest_reminder_audio_filename_str = i_rest_reminder_audio_filename
        self.rest_reminder_volume_int = i_rest_reminder_volume
        self.rest_reminder_notification_type_int = i_rest_reminder_notification_type
        self.breathing_reminder_active_bool = True if i_breathing_reminder_active else False
        self.breathing_reminder_interval_int = i_breathing_reminder_interval
        self.breathing_reminder_audio_filename_str = i_breathing_reminder_audio_filename
        self.breathing_reminder_audio_volume_int = i_breathing_reminder_audio_volume
        self.breathing_reminder_notification_type_int = i_breathing_reminder_notification_type
        self.breathing_reminder_phrase_setup_int = i_breathing_reminder_phrase_setup
        self.breathing_reminder_nr_before_dialog_int = i_breathing_reminder_nr_before_dialog
        self.breathing_reminder_dialog_audio_active_bool = True if i_breathing_reminder_dialog_audio_active else False
        self.breathing_reminder_dialog_close_on_active_bool = \
            True if i_breathing_reminder_dialog_close_on_active else False
        self.breathing_reminder_text_str = i_breathing_reminder_text
        self.breathing_dialog_phrase_selection_int = i_breathing_dialog_phrase_selection
        self.prep_reminder_audio_filename_str = i_prep_reminder_audio_filename
        self.prep_reminder_audio_volume_int = i_prep_reminder_audio_volume
        self.run_on_startup_bool = True if i_run_on_startup else False
        self.nr_times_started_since_last_feedback_notif_int = i_nr_times_started_since_last_feedback_notif

    @property
    def nr_times_started_since_last_feedback_notif(self):
        return self.nr_times_started_since_last_feedback_notif_int

    @nr_times_started_since_last_feedback_notif.setter
    def nr_times_started_since_last_feedback_notif(self, i_new_nr_times_started_since_last_feedback_notif: int):
        self.nr_times_started_since_last_feedback_notif_int = i_new_nr_times_started_since_last_feedback_notif
        self._update(
            db.Schema.SettingsTable.Cols.nr_times_started_since_last_feedback_notif,
            i_new_nr_times_started_since_last_feedback_notif
        )

    @property
    def breathing_reminder_notification_type(self):
        ret_breathing_notification_type_enum = mc.mc_global.NotificationType(
            self.breathing_reminder_notification_type_int
        )
        return ret_breathing_notification_type_enum

    @property
    def prep_reminder_audio_volume(self) -> int:
        return self.prep_reminder_audio_volume_int

    @prep_reminder_audio_volume.setter
    def prep_reminder_audio_volume(self, i_new_prep_reminder_audio_volume):
        self.prep_reminder_audio_volume_int = i_new_prep_reminder_audio_volume
        self._update(
            db.Schema.SettingsTable.Cols.prep_reminder_audio_volume,
            i_new_prep_reminder_audio_volume
        )

    @property
    def prep_reminder_audio_filename(self) -> str:
        return self.prep_reminder_audio_filename_str

    @prep_reminder_audio_filename.setter
    def prep_reminder_audio_filename(self, i_new_prep_reminder_audio_filename: str):
        self.prep_reminder_audio_filename_str = i_new_prep_reminder_audio_filename
        self._update(
            db.Schema.SettingsTable.Cols.prep_reminder_audio_filename,
            i_new_prep_reminder_audio_filename
        )

    @property
    def breathing_dialog_phrase_selection(self) -> mc.mc_global.PhraseSelection:
        ret_phrase_selection = mc.mc_global.PhraseSelection(self.breathing_dialog_phrase_selection_int)
        return ret_phrase_selection

    @property
    def rest_reminder_active(self) -> bool:
        return self.rest_reminder_active_bool

    @rest_reminder_active.setter
    def rest_reminder_active(self, i_new_is_active: bool) -> None:
        new_is_active_as_int = db.SQLITE_TRUE_INT if i_new_is_active else db.SQLITE_FALSE_INT
        self._update(
            db.Schema.SettingsTable.Cols.rest_reminder_active,
            new_is_active_as_int
        )

    @property
    def rest_reminder_interval(self) -> int:
        return self.rest_reminder_interval_int

    @rest_reminder_interval.setter
    def rest_reminder_interval(self, i_new_interval: int) -> None:
        self.rest_reminder_interval = i_new_interval
        self._update(
            db.Schema.SettingsTable.Cols.rest_reminder_interval,
            i_new_interval
        )

    @property
    def rest_reminder_audio_filename(self) -> str:
        return self.rest_reminder_audio_filename

    @rest_reminder_audio_filename.setter
    def rest_reminder_audio_filename(self, i_new_filename: str) -> None:
        self.rest_reminder_audio_filename_str = i_new_filename
        self._update(
            db.Schema.SettingsTable.Cols.rest_reminder_audio_filename,
            i_new_filename
        )

    @property
    def rest_reminder_volume(self) -> int:
        return self.rest_reminder_volume_int

    @rest_reminder_volume.setter
    def rest_reminder_volume(self, i_new_volume: int) -> None:
        self.rest_reminder_volume_int = i_new_volume
        self._update(
            db.Schema.SettingsTable.Cols.rest_reminder_volume,
            i_new_volume
        )

    # rest_reminder_notification_type_int

    @property
    def rest_reminder_notification_type(self) -> mc.mc_global.NotificationType:
        ret_notification_type = mc.mc_global.NotificationType(self.rest_reminder_notification_type_int)
        return ret_notification_type

    @rest_reminder_notification_type.setter
    def rest_reminder_notification_type(
        self,
        i_new_notification_type: mc.mc_global.NotificationType
    ) -> None:
        self.rest_reminder_notification_type_int = i_new_notification_type.value
        self._update(
            db.Schema.SettingsTable.Cols.rest_reminder_notification_type,
            i_new_notification_type.value
        )

    @property
    def run_on_startup(self) -> bool:
        return self.run_on_startup_bool

    @run_on_startup.setter
    def run_on_startup(self, i_new_run_on_startup: bool) -> None:
        new_run_on_startup_as_int = db.SQLITE_TRUE_INT if i_new_run_on_startup else db.SQLITE_FALSE_INT
        self._update(
            db.Schema.SettingsTable.Cols.run_on_startup,
            new_run_on_startup_as_int
        )

    @staticmethod
    def _update(i_col_name: str, i_new_value: typing.Any) -> None:
        db_exec(
            "UPDATE " + db.Schema.SettingsTable.name
            + " SET " + i_col_name + " = ?"
            + " WHERE " + db.Schema.SettingsTable.Cols.id + " = ?",
            (i_new_value, str(db.SINGLE_SETTINGS_ID_INT))
        )

    @staticmethod
    def get():
        db_connection = db.Helper.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor_result = db_cursor.execute(
            "SELECT * FROM " + db.Schema.SettingsTable.name
            + " WHERE " + db.Schema.SettingsTable.Cols.id + "=?",
            (str(db.SINGLE_SETTINGS_ID_INT),)
        )
        settings_db_te = db_cursor_result.fetchone()
        db_connection.commit()

        return SettingsM(*settings_db_te)
        # -the asterisk (*) will "expand" the tuple into separate arguments for the function header

    @staticmethod
    def update_rest_reminder_audio_filename(i_new_audio_filename: str) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.rest_reminder_audio_filename,
            i_new_audio_filename
        )

    @staticmethod
    def update_breathing_dialog_close_on_hover(i_close_on_active: bool) -> None:
        new_value_bool_as_int = db.SQLITE_TRUE_INT if i_close_on_active else db.SQLITE_FALSE_INT
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_dialog_close_on_hover,
            new_value_bool_as_int
        )

    @staticmethod
    def update_breathing_dialog_audio_active(i_audio_active: bool) -> None:
        new_value_bool_as_int = db.SQLITE_TRUE_INT if i_audio_active else db.SQLITE_FALSE_INT
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_dialog_audio_active,
            new_value_bool_as_int
        )

    @staticmethod
    def update_rest_reminder_volume(i_new_volume: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.rest_reminder_volume,
            i_new_volume
        )

    @staticmethod
    def update_rest_reminder_notification_type(i_new_notification_type: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.rest_reminder_notification_type,
            i_new_notification_type
        )

    @staticmethod
    def update_rest_reminder_active(i_reminder_active: bool) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.rest_reminder_active,
            db.SQLITE_TRUE_INT if i_reminder_active else db.SQLITE_FALSE_INT
        )

    @staticmethod
    def update_rest_reminder_interval(i_reminder_interval: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.rest_reminder_interval,
            i_reminder_interval
        )

    @staticmethod
    def update_breathing_reminder_active(i_reminder_active: bool) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_active,
            db.SQLITE_TRUE_INT if i_reminder_active else db.SQLITE_FALSE_INT
        )

    @staticmethod
    def update_breathing_reminder_interval(i_reminder_interval: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_interval,
            i_reminder_interval
        )

    @staticmethod
    def update_prep_reminder_audio_filename(i_new_audio_filename: str) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.prep_reminder_audio_filename,
            i_new_audio_filename
        )

    @staticmethod
    def update_breathing_reminder_audio_filename(i_new_audio_filename: str) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_audio_filename,
            i_new_audio_filename
        )

    @staticmethod
    def update_breathing_reminder_volume(i_new_volume: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_volume,
            i_new_volume
        )

    @staticmethod
    def update_prep_reminder_audio_volume(i_new_volume: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.prep_reminder_audio_volume,
            i_new_volume
        )

    @staticmethod
    def update_breathing_reminder_nr_per_dialog(i_new_nr_per_dialog: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_nr_before_dialog,
            i_new_nr_per_dialog
        )

    @staticmethod
    def update_breathing_reminder_notification_type(i_new_notification_type: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_notification_type,
            i_new_notification_type
        )

    @staticmethod
    def update_breathing_reminder_notification_phrase_setup(i_new_phrase_setup: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_reminder_phrase_setup,
            i_new_phrase_setup
        )

    @staticmethod
    def update_breathing_dialog_phrase_selection(i_new_phrase_selection: int) -> None:
        SettingsM._update(
            db.Schema.SettingsTable.Cols.breathing_dialog_phrase_selection,
            i_new_phrase_selection
        )


def export_all() -> str:
    date_sg = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path_str = mc.mc_global.get_user_files_path(date_sg + "_exported.csv")
    csv_writer = csv.writer(open(file_path_str, "w"))

    """
    csv_writer.writeheader(
        "Title", "In-breath phrase", "Out-breath phrase", "Shortened in-breath phrase", "Shortened out-breath phrase"
    )
    """

    csv_writer.writerow(("",))
    csv_writer.writerow(("===== Breathing Phrases =====",))
    for phrase in PhrasesM.get_all():
        csv_writer.writerow((phrase.title, phrase.ib, phrase.ob, phrase.ib_short, phrase.ob_short))

    csv_writer.writerow(("",))
    csv_writer.writerow(("===== Rest Actions =====",))
    for rest_action in RestActionsM.get_all():
        csv_writer.writerow((rest_action.title,))

    return file_path_str


def populate_db_with_setup_data() -> None:
    PhrasesM.add(
        "In, Out",
        "Breathing in, I know I am breathing in",
        "Breathing out, I know I am breathing out",
        "in",
        "out",
        mc.mc_global.BreathingPhraseType.in_out
    )
    PhrasesM.add(
        "Aware of Body",
        "Aware of my body, I breathe in",
        "Aware of my body, I breathe out",
        "body, in",
        "body, out",
        mc.mc_global.BreathingPhraseType.in_out
    )
    PhrasesM.add(
        "Caring, Relaxing",
        "Breathing in, I care for my body",
        "Breathing out, I relax my body",
        "caring",
        "relaxing",
        mc.mc_global.BreathingPhraseType.in_out
    )
    PhrasesM.add(
        "Happy, At Peace",
        "May I be happy",
        "May I be peaceful",
        "happy",
        "peaceful",
        mc.mc_global.BreathingPhraseType.in_out
    )
    PhrasesM.add(
        "Sharing, Contributing",
        "Breathing in I share the well-being of others",
        "Breathing out I contribute to the well-being of others",
        "sharing well-being",
        "contributing to well-being",
        mc.mc_global.BreathingPhraseType.in_out
    )

    """
    PhrasesM.add(
        "Compassion",
        "Breathing in compassion to myself",
        "Breathing out compassion to others",
        "compassion to myself",
        "compassion to others",
        mc.mc_global.BreathingPhraseType.in_out
    )
    PhrasesM.add(
        "Self-love and acceptance",
        "I love and accept myself just as I am",
        "",
        "Self-love",
        "",
        mc.mc_global.BreathingPhraseType.single
    )
    """

    RestActionsM.add("Making a cup of tea")
    RestActionsM.add("Filling a water bottle for my desk")
    RestActionsM.add("Stretching my arms")
    RestActionsM.add("Opening a window")
    RestActionsM.add("Watering the plants")
    RestActionsM.add("Cleaning/organizing my space")
    RestActionsM.add("Eating something healthy")
    RestActionsM.add("Slow mindful walking inside")
    RestActionsM.add("Walking outside")


def populate_db_with_test_data() -> None:
    populate_db_with_setup_data()
