# Preprocessing

LANGUAGE=python
BASE_DIR=../data
LOG_DIR=$BASE_DIR/log/$LANGUAGE

SUBMISSIONS_FILE_CSV=solutions_python3.csv
SUBMISSIONS_WITH_RAW_ISSUES_FILE_CSV=solutions_unique_with_raw_issues_python3.csv
RAW_ISSUES_FILE_CSV=raw_issues.csv
SUBMISSIONS_WITH_QODANA_ISSUES_FILE_CSV=solutions_unique_with_qodana_issues_python3.csv
QODANA_ISSUES_FILE_CSV=qodana_issues.csv
USERS_FILE_CSV=users.csv
STEPS_FILE_CSV=steps.csv
TOPICS_FILE_CSV=topics.csv
USERS_TO_SUBMISSIONS=submission_to_user_anon.csv


echo "Start submissions preprocessing..."
python3 preprocessing/preprocess_submissions.py $BASE_DIR/input/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                                $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                                --users-to-submissions-path $BASE_DIR/input/$LANGUAGE/$USERS_TO_SUBMISSIONS \
                                                --log-path $LOG_DIR

echo "Start raw issues preprocessing..."
python3 preprocessing/preprocess_issues.py raw_issues \
                                           $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                           $BASE_DIR/input/$LANGUAGE/$SUBMISSIONS_WITH_RAW_ISSUES_FILE_CSV \
                                           $BASE_DIR/output/$LANGUAGE/$RAW_ISSUES_FILE_CSV \
                                           --ignore-issue-classes CyclomaticComplexityCheck JavaNCSSCheck \
                                           --log-path $LOG_DIR

#echo "Start qodana issues preprocessing..."
#python3 preprocessing/preprocess_issues.py qodana_issues \
#                                           $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
#                                           $BASE_DIR/input/$LANGUAGE/$SUBMISSIONS_WITH_QODANA_ISSUES_FILE_CSV \
#                                           $BASE_DIR/output/$LANGUAGE/$QODANA_ISSUES_FILE_CSV \
#                                           --ignore-issue-classes JavaAnnotator WrongPackageStatement \
#                                           --log-path $LOG_DIR

echo "Start topics preprocessing..."
python3 preprocessing/preprocess_topics.py $BASE_DIR/input/$LANGUAGE/$TOPICS_FILE_CSV \
                                           $BASE_DIR/output/$LANGUAGE/$TOPICS_FILE_CSV \
                                           --log-path $LOG_DIR
echo "Start steps preprocessing..."
python3 preprocessing/preprocess_steps.py $BASE_DIR/input/$LANGUAGE/$STEPS_FILE_CSV \
                                         $BASE_DIR/output/$LANGUAGE/$TOPICS_FILE_CSV \
                                         $BASE_DIR/output/$LANGUAGE/$STEPS_FILE_CSV \
                                         --log-path $LOG_DIR
echo "Start users preprocessing..."
python3 preprocessing/preprocess_users.py $BASE_DIR/input/$LANGUAGE/$USERS_FILE_CSV \
                                          $BASE_DIR/output/$LANGUAGE/$USERS_FILE_CSV \
                                          --log-path $LOG_DIR
echo "Start dataset compilation..."
python3 preprocessing/compile_dataset.py $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                         $BASE_DIR/output/$LANGUAGE/$STEPS_FILE_CSV \
                                         $BASE_DIR/output/$LANGUAGE/$TOPICS_FILE_CSV \
                                         $BASE_DIR/output/$LANGUAGE/$USERS_FILE_CSV \
                                         --log-path $LOG_DIR

# Statistics
echo "Stats submission metrics..."
python3 statistics/submissions_metrics_statistics.py $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                                     $BASE_DIR/output/$LANGUAGE/submissions_metrics.csv \
                                                     --log-path $LOG_DIR
echo "Stats submission client stats..."
python3 statistics/client_statistics.py $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                        $BASE_DIR/output/$LANGUAGE/submissions_client_stats.csv \
                                        --log-path $LOG_DIR
echo "Stats submission raw issues stats..."
python3 statistics/issues_statistics.py raw_issues \
                                        $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                        $BASE_DIR/output/$LANGUAGE/$RAW_ISSUES_FILE_CSV \
                                        $BASE_DIR/output/$LANGUAGE/raw_issues_stats.csv \
                                        --log-path $LOG_DIR
#echo "Stats submission qodana issues stats..."
#python3 statistics/issues_statistics.py qodana_issues \
#                                        $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
#                                        $BASE_DIR/output/$LANGUAGE/$QODANA_ISSUES_FILE_CSV \
#                                        $BASE_DIR/output/$LANGUAGE/qodana_issues_stats.csv \
#                                        --log-path $LOG_DIR

echo "Stats submission raw issues by steps stats..."
python3 statistics/issues_steps_statistics.py $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
                                              $BASE_DIR/output/$LANGUAGE/raw_issues_stats.csv \
                                              $BASE_DIR/output/$LANGUAGE/$RAW_ISSUES_FILE_CSV \
                                              $BASE_DIR/output/$LANGUAGE/raw_issues_steps_stats.csv \
                                              --log-path $LOG_DIR
#echo "Stats submission qodana issues by steps stats..."
#python3 statistics/issues_steps_statistics.py $BASE_DIR/output/$LANGUAGE/$SUBMISSIONS_FILE_CSV \
#                                              $BASE_DIR/output/$LANGUAGE/qodana_issues_stats.csv \
#                                              $BASE_DIR/output/$LANGUAGE/$QODANA_ISSUES_FILE_CSV \
#                                              $BASE_DIR/output/$LANGUAGE/qodana_issues_steps_stats.csv \
#                                              --log-path $LOG_DIR

#echo "Stats submission raw issues change stats..."
#python3 statistics/issues_change_statistics.py prep_data/submissions.csv prep_data/raw_issues_stats.csv prep_data/raw_issues.csv prep_data/raw_issues_change_stats.csv
#echo "Stats submission qodana issues change stats..."
#python3 statistics/issues_change_statistics.py prep_data/submissions.csv prep_data/qodana_issues_stats.csv prep_data/qodana_issues.csv prep_data/qodana_issues_change_stats.csv