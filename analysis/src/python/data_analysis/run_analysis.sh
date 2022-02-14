# Preprocessing
echo "Start submissions preprocessing..."
python3 preprocessing/preprocess_submissions.py data/submissions.csv prep_data/submissions.csv --users-to-submissions-path data/submission_to_user_anon.csv
echo "Start raw issues preprocessing..."
python3 preprocessing/preprocess_issues.py raw_issues prep_data/submissions.csv  data/unique_submissions_raw_issues.csv prep_data/raw_issues.csv --ignore-issue-classes CyclomaticComplexityCheck JavaNCSSCheck
echo "Start qodana issues preprocessing..."
python3 preprocessing/preprocess_issues.py qodana_issues prep_data/submissions.csv  data/unique_submissions_qodana_issues.csv prep_data/qodana_issues.csv --ignore-issue-classes JavaAnnotator WrongPackageStatement
echo "Start topics preprocessing..."
python3 preprocessing/preprocess_topics.py data/topics.csv  prep_data/topics.csv
echo "Start steps preprocessing..."
python3 reprocessing/preprocess_steps.py data/steps.csv  prep_data/topics.csv prep_data/steps.csv
echo "Start users preprocessing..."
python3 preprocessing/preprocess_users.py data/users.csv  prep_data/users.csv
echo "Start dataset compilation..."
python3 preprocessing/compile_dataset.py prep_data/submissions.csv prep_data/steps.csv prep_data/topics.csv prep_data/users.csv

# Statistics
echo "Stats submission metrics..."
python3 statistics/submissions_metrics_statistics.py prep_data/submissions.csv prep_data/submissions_metrics.csv
echo "Stats submission client stats..."
python3 statistics/client_statistics.py prep_data/submissions.csv prep_data/submissions_client_stats.csv
echo "Stats submission raw issues stats..."
python3 statistics/issues_statistics.py raw_issues prep_data/submissions.csv prep_data/raw_issues.csv prep_data/raw_issues_stats.csv
echo "Stats submission qodana issues stats..."
python3 statistics/issues_statistics.py qodana_issues prep_data/submissions.csv prep_data/qodana_issues.csv prep_data/qodana_issues_stats.csv
echo "Stats submission raw issues change stats..."
python3 statistics/issues_change_statistics.py prep_data/submissions.csv prep_data/raw_issues_stats.csv prep_data/raw_issues.csv prep_data/raw_issues_change_stats.csv
echo "Stats submission qodana issues change stats..."
python3 statistics/issues_change_statistics.py prep_data/submissions.csv prep_data/qodana_issues_stats.csv prep_data/qodana_issues.csv prep_data/qodana_issues_change_stats.csv
echo "Stats submission raw issues by steps stats..."
python3 statistics/issues_steps_statistics.py prep_data/submissions.csv prep_data/raw_issues_stats.csv prep_data/raw_issues.csv prep_data/raw_issues_steps
echo "Stats submission qodana issues by steps stats..."
python3 statistics/issues_steps_statistics.py prep_data/submissions.csv prep_data/qodana_issues_stats.csv prep_data/qodana_issues.csv prep_data/qodana_issues_steps
