/** @file tune.h
 *
 * Header declaring the functions that support the @tune function and
 * dealing with tunable configuration parameters.
 *
 * This file is part of Fuzzball MUCK.  Please see LICENSE.md for details.
 */

#ifndef _TUNE_H
#define _TUNE_H

#include "array.h"

#define TUNESET_SUCCESS         0   /* success                  */
#define TUNESET_SUCCESS_DEFAULT 5   /* success, set to default  */
#define TUNESET_UNKNOWN         1   /* unrecognized sysparm     */
#define TUNESET_SYNTAX          2   /* bad value syntax         */
#define TUNESET_BADVAL          3   /* bad value                */
#define TUNESET_DENIED          4   /* mucker level too low     */

/* Tunable defaults management */

/* Tunable parameter names must not start with TP_FLAG_DEFAULT or they won't be saved. */
#define TP_FLAG_DEFAULT '%'

/* True if parameter starts with default flag, otherwise false */
#define TP_HAS_FLAG_DEFAULT(param) (param != NULL && param[0] == TP_FLAG_DEFAULT)

/* If specified, remove the reset to default flag by incrementing past it */
#define TP_CLEAR_FLAG_DEFAULT(param) if (TP_HAS_FLAG_DEFAULT(param)) { param++; }

/* These externs are defined defined in tunelist.h
 *
 * They contain the values associated with each tune variable, as a short
 * cut for C code that wants quick and easy access to the variables.
 *
 * This is the case for all these similar tp_ named externs in this file,
 * so they will not be individually documented.
 */
extern const char *tp_autolook_cmd;
extern const char *tp_cpennies;
extern const char *tp_cpenny;
extern const char *tp_description_default;
extern const char *tp_dumping_mesg;
extern const char *tp_dumpdone_mesg;
extern const char *tp_dumpwarn_mesg;
extern const char *tp_file_connection_help;
extern const char *tp_file_credits;
extern const char *tp_file_editor_help;
extern const char *tp_file_help;
extern const char *tp_file_help_dir;
extern const char *tp_file_info_dir;
extern const char *tp_file_log_cmd_times;
extern const char *tp_file_log_commands;
extern const char *tp_file_log_gripes;
extern const char *tp_file_log_malloc;
extern const char *tp_file_log_muf_errors;
extern const char *tp_file_log_programs;
extern const char *tp_file_log_sanfix;
extern const char *tp_file_log_sanity;
extern const char *tp_file_log_status;
extern const char *tp_file_log_stderr;
extern const char *tp_file_log_stdout;
extern const char *tp_file_log_user;
extern const char *tp_file_man;
extern const char *tp_file_man_dir;
extern const char *tp_file_mpihelp;
extern const char *tp_file_mpihelp_dir;
extern const char *tp_file_motd;
extern const char *tp_file_news;
extern const char *tp_file_news_dir;
extern const char *tp_file_sysparms;
extern const char *tp_file_parameters;
extern const char *tp_file_welcome_screen;
extern const char *tp_gender_prop;
extern const char *tp_huh_mesg;
extern const char *tp_idle_mesg;
extern const char *tp_leave_mesg;
extern const char *tp_muckname;
extern const char *tp_pcreate_flags;
extern const char *tp_pennies;
extern const char *tp_penny;
extern const char *tp_playermax_bootmesg;
extern const char *tp_playermax_warnmesg;
extern const char *tp_register_mesg;
extern const char *tp_reserved_names;
extern const char *tp_reserved_player_names;
extern const char *tp_ssl_cert_file;
extern const char *tp_ssl_key_file;
extern const char *tp_ssl_keyfile_passwd;
extern const char *tp_ssl_cipher_preference_list;
extern const char *tp_ssl_min_protocol_version;

/* For a tune-able string entry */
struct tune_str_entry {
    const char *group;          /* Tune group               */
    const char *name;           /* Parameter name           */
    const char **str;           /* Parameter value          */
    int readmlev;               /* MUCKER level to read     */
    int writemlev;              /* MUCKER level to write    */
    const char *label;          /* Label text               */
    char *module;               /* Module                   */
    int isnullable;             /* Can be null?             */
    int isdefault;              /* Is set to default value? */
    const char *defaultstr;     /* Default value            */
};

/* This is the master list of tune list parameters (string) which
 * is defined in tunelist.h.
 */
extern struct tune_str_entry tune_str_list[];

extern int tp_aging_time;
extern int tp_clean_interval;
extern int tp_dump_interval;
extern int tp_dump_warntime;
extern int tp_idle_ping_time;
extern int tp_maxidle;
extern int tp_pname_history_threshold;

struct tune_time_entry {
    const char *group;          /* Tune group               */
    const char *name;           /* Parameter name           */
    int *tim;                   /* The time value           */
    int readmlev;               /* MUCKER level to read     */
    int writemlev;              /* MUCKER level to write    */
    const char *label;          /* Label text               */
    char *module;               /* Module                   */
    int isdefault;              /* Is set to default value? */
    const int defaulttim;       /* Default value            */
};

/* This is the master list of tune list parameters (time) which
 * is defined in tunelist.h.
 */
extern struct tune_time_entry tune_time_list[];

extern int tp_addpennies_muf_mlev;
extern int tp_cmd_log_threshold_msec;
extern int tp_commands_per_time;
extern int tp_command_burst_size;
extern int tp_command_time_msec;
extern int tp_exit_cost;
extern int tp_free_frames_pool;
extern int tp_instr_slice;
extern int tp_kill_base_cost;
extern int tp_kill_bonus;
extern int tp_kill_min_cost;
extern int tp_link_cost;
extern int tp_listen_mlev;
extern int tp_lookup_cost;
extern int tp_max_force_level;
extern int tp_max_instr_count;
extern int tp_max_loaded_objs;
extern int tp_max_ml4_preempt_count;
extern int tp_max_ml4_nested_interp_loop_count;
extern int tp_max_nested_interp_loop_count;
extern int tp_max_plyr_processes;
extern int tp_max_process_limit;
extern int tp_max_object_endowment;
extern int tp_max_output;
extern int tp_max_pennies;
extern int tp_mcp_muf_mlev;
extern int tp_movepennies_muf_mlev;
extern int tp_mpi_max_commands;
extern int tp_object_cost;
extern int tp_pause_min;
extern int tp_pennies_muf_mlev;
extern int tp_penny_rate;
extern int tp_player_name_limit;
extern int tp_playermax_limit;
extern int tp_process_timer_limit;
extern int tp_room_cost;
extern int tp_start_pennies;
extern int tp_userlog_mlev;

struct tune_val_entry {
    const char *group;          /* Tune group               */
    const char *name;           /* Parameter name           */
    int *val;                   /* The integer value        */
    int readmlev;               /* MUCKER level to read     */
    int writemlev;              /* MUCKER level to write    */
    const char *label;          /* Label text               */
    char *module;               /* Module                   */
    int isdefault;              /* Is set to default value? */
    const int defaultval;       /* Default value            */
};

/* This is the master list of tune list parameters (integer) which
 * is defined in tunelist.h.
 */
extern struct tune_val_entry tune_val_list[];

extern dbref tp_default_room_parent;
extern dbref tp_lost_and_found;
extern dbref tp_player_start;
extern dbref tp_toad_default_recipient;

struct tune_ref_entry {
    const char *group;          /* Tune group               */
    const char *name;           /* Parameter name           */
    int typ;                    /* DB type restriction      */
    dbref *ref;                 /* The dbref value          */
    int readmlev;               /* MUCKER level to read     */
    int writemlev;              /* MUCKER level to write    */
    const char *label;          /* Label text               */
    char *module;               /* Module                   */
    int isdefault;              /* Is set to default value? */
    const dbref defaultref;     /* Default value            */
};

/* This is the master list of tune list parameters (dbref) which
 * is defined in tunelist.h.
 */
extern struct tune_ref_entry tune_ref_list[];

extern int tp_7bit_other_names;
extern int tp_7bit_thing_names;
extern int tp_allow_home;
extern int tp_autolink_actions;
extern int tp_cipher_server_preference;
extern int tp_compatible_priorities;
extern int tp_consistent_lock_source;
extern int tp_dark_sleepers;
extern int tp_dbdump_warning;
extern int tp_diskbase_propvals;
extern int tp_do_mpi_parsing;
extern int tp_dumpdone_warning;
extern int tp_enable_match_yield;
extern int tp_enable_prefix;
extern int tp_exit_darking;
extern int tp_expanded_debug;
extern int tp_force_mlev1_name_notify;
extern int tp_hostnames;
extern int tp_idleboot;
extern int tp_idle_ping_enable;
extern int tp_ignore_bidirectional;
extern int tp_ignore_support;
extern int tp_listeners;
extern int tp_listeners_env;
extern int tp_listeners_obj;
extern int tp_lock_envcheck;
extern int tp_log_commands;
extern int tp_log_failed_commands;
extern int tp_log_interactive;
extern int tp_log_programs;
extern int tp_m3_huh;
extern int tp_muf_comments_strict;
extern int tp_optimize_muf;
extern int tp_periodic_program_purge;
extern int tp_playermax;
extern int tp_pname_history_reporting;
extern int tp_quiet_moves;
extern int tp_realms_control;
extern int tp_recognize_null_command;
extern int tp_registration;
extern int tp_tab_input_replaced_with_space;
extern int tp_restrict_kill;
extern int tp_secure_teleport;
extern int tp_secure_who;
extern int tp_show_legacy_props;
extern int tp_starttls_allow;
extern int tp_strict_god_priv;
extern int tp_teleport_to_player;
extern int tp_thing_darking;
extern int tp_thing_movement;
extern int tp_toad_recycle;
extern int tp_verbose_clone;
extern int tp_verbose_examine;
extern int tp_who_hides_dark;
extern int tp_wiz_vehicles;
extern int tp_zombies;

struct tune_bool_entry {
    const char *group;          /* Tune group               */
    const char *name;           /* Parameter name           */
    int *boolval;               /* Boolean value            */
    int readmlev;               /* MUCKER level to read     */
    int writemlev;              /* MUCKER level to write    */
    const char *label;          /* Label text               */
    char *module;               /* Module                   */
    int isdefault;              /* Is set to default value? */
    const int defaultbool;      /* Default value            */
};

/* This is the master list of tune list parameters (boolean) which
 * is defined in tunelist.h.
 */
extern struct tune_bool_entry tune_bool_list[];

/**
 * This takes an object and a string of flags, and sets them on the object
 *
 * The tunestr can have the following characters in it.  Each corresponds
 * to a flag.  Unknown flags are ignored.  'W' (wizard) cannot be set and
 * will be ignored.
 *
 * 0 1 2 3 A B C D G H J K L M Q S V X Y O Z
 *
 * Each corresponds to the first letter of the flag in question, with the
 * numbers being MUCKER levels.
 *
 * @param obj the object to set flags on
 * @param tunestr the string of flags
 */
void set_flags_from_tunestr(dbref obj, const char *flags);

/**
 * Count all available tune parameters.
 *
 * This is complicated by the fact that different parameter types are in
 * different arrays.
 *
 * @return integer number of tune paramters.
 */
int tune_count_parms(void);

/**
 * Free all tune parameters
 *
 * This will probably render the MUCK unstable if casually used; it is
 * for the MUCK shutdown process and is, in fact, one the last cleanups
 * called.
 */
void tune_freeparms(void);

/**
 * Get the string value of a given parameter
 *
 * The 'name' must match a parameter value, case insensitive.  If
 * it does not match a null string is returned.  If 'name' has
 * the default value prefix, that prefix is removed first.
 *
 * mlev is the player's MUCKER level for security checking.  If
 * security check fails, an empty string is returned.
 *
 * The string is in a static buffer, so this is not thread safe
 * and you must copy it if you want to ensure it doesn't mutate
 * out from under you.
 *
 * DBREFs will be prefixed with #, and booleans will return as "yes"
 * or "no".  Time will be a number in seconds.
 *
 * @param name the name of the parameter
 * @param mlev the MUCKER level of the calling player.
 * @return string as specified above.
 */
const char *tune_get_parmstring(const char *name, int mlev);

/**
 * Load default parameters into the global tune structures.
 *
 * This initializes all the global tune structures with default
 * values, marking each as isdefault=1 in the process.  If there
 * is an existing string value in a string tune setting, it will be
 * free'd (if not isdefault)
 *
 * This is a pretty destructive call.
 */
void tune_load_parms_defaults(void);

/**
 * Load tune params from a file.
 *
 * This loads the parameters from a file in the format written
 * by tune_save_parms_to_file.  It ignores lines that start with a #
 * mark.
 *
 * @see tune_save_parms_to_file
 * @see tune_setparm
 *
 * It will read up to 'cnt' number of lines, or all lines in the file if
 * cnt is a negative number.
 *
 * Player may either be NOTHING, or a player that will receive notifications.
 * The tune settings are done with MLEV_GOD no matter what MUCKER level
 * 'player' actually has.  If player is NOTHING, the process is silent.
 *
 * @param f the file handle to read from
 * @param player The player who will receive notifications, or NOTHING
 * @param cnt the count of lines to read or -1 to read all lines.
 */
void tune_load_parms_from_file(FILE * f, dbref player, int cnt);

/**
 * Creates a MUF PACKED (sequential) array from the tune parameters.
 *
 * Takes an optional pattern which is used a name search; "" matches
 * everything.
 *
 * @see equalstr
 *
 * mlevel is the MUCKER level of the person doing the call for
 * permission checking.  Pinned is sent directly to new_array_packed
 *
 * @see new_array_packed
 *
 * The resulting array is an array of dictionaries.  The dictionaries
 * vary slightly in structure based on the "type" of tune data.  In
 * common, they have the following fields:
 *
 * type - boolean, timespan, integer, dbref, string
 * group - the tune group this parameter belongs to
 * name - the name of the parameter
 * value - the value of the parameter
 * mlev - the MUCKER level required to read this parameter.
 * readmlev - the same as mlev
 * writemlev - the MUCKER level required to write this paramter.
 * label - some label text to explain the parameter
 * default - the default value
 * active - if this tune parameter is 'active' or applies to the MUCK
 * nullable - is this field able to be null?
 *
 * It may additionally have 'objtype', for type == dbref, which will
 * be 'any', 'player', 'thing', 'room', 'exit', 'program', 'garbage',
 * or 'unknown'
 *
 * @param pattern the pattern to search for
 * @param mlev the MUCKER level of the calling player
 * @param pinned pin the array?
 * @return a packed stk_array type - you are responsible to free this memory
 */
stk_array *tune_parms_array(const char *pattern, int mlev, int pinned);

/**
 * Save tune parameters to a file
 *
 * Some notes on parameter saving:
 *
 * Comment out default values saved to the output.  This allows distinguishing
 * between available parameters and customized parameters while still creating
 * a list of new parameters in fresh or updated databases.
 *
 * If value is specified, save it as normal.  It won't be marked as default
 * again until it's removed from the database (including commenting it out).
 *
 * Example:
 * > Custom
 * ssl_min_protocol_version=TLSv1.2
 * > Default
 * %ssl_min_protocol_version=None
 *
 * @param f the file handle to write to
 */
void tune_save_parms_to_file(FILE * f);

/**
 * Sets a tune parameter and handles all the intricaties therein
 *
 * For a given player 'player' with MUCKER level 'mlev', it will set
 * parameter 'parmname' to 'val', doing all necessary parsing.
 *
 * This will return one of the following integer constants:
 *
 * TUNESET_DENIED - permission denied
 * TUNESET_SUCCESS - success
 * TUNESET_SUCCESS_DEFAULT - successfully reset to default
 * TUNESET_UNKNOWN - unknown parmname
 * TUNESET_BADVAL - bad (invalid) value for parameter
 * TUNESET_SYNTAX - syntax error for val
 *
 * @param player the player doing the call
 * @param parmname the parameter to set
 * @param val the value to set the parameter to
 * @param mlev the MUCKER level of the player doing the call
 * @return integer result, as described above.
 */
int tune_setparm(dbref player, const char *parmname, const char *val, int security);

#endif  /* _TUNE_H */
