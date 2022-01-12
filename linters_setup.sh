export LINTERS_DIRECTORY=/opt/linters

export CHECKSTYLE_VERSION=8.44
export CHECKSTYLE_DIRECTORY=${LINTERS_DIRECTORY}/checkstyle

export DETEKT_VERSION=1.14.2
export DETEKT_DIRECTORY=${LINTERS_DIRECTORY}/detekt

export PMD_VERSION=6.36.0
export PMD_DIRECTORY=${LINTERS_DIRECTORY}/pmd

mkdir -p ${LINTERS_DIRECTORY} && chmod -R 777 ${LINTERS_DIRECTORY}

mkdir -p ${CHECKSTYLE_DIRECTORY} && mkdir -p ${DETEKT_DIRECTORY} && mkdir -p ${PMD_DIRECTORY}

apt -y update && apt -y upgrade

# Install curl and unzip
apt -y install curl unzip

# Install Detekt and Detekt-formatting
curl -sSLO https://github.com/detekt/detekt/releases/download/v${DETEKT_VERSION}/detekt-cli-${DETEKT_VERSION}.zip \
    && unzip detekt-cli-${DETEKT_VERSION}.zip -d ${DETEKT_DIRECTORY} \
    &&  curl -H "Accept: application/zip" https://repo.maven.apache.org/maven2/io/gitlab/arturbosch/detekt/detekt-formatting/${DETEKT_VERSION}/detekt-formatting-${DETEKT_VERSION}.jar -o ${DETEKT_DIRECTORY}/detekt-formatting-${DETEKT_VERSION}.jar

# Install Checkstyle
curl -L https://github.com/checkstyle/checkstyle/releases/download/checkstyle-${CHECKSTYLE_VERSION}/checkstyle-${CHECKSTYLE_VERSION}-all.jar > ${CHECKSTYLE_DIRECTORY}/checkstyle-${CHECKSTYLE_VERSION}-all.jar

# Install PMD
curl -sSLO https://github.com/pmd/pmd/releases/download/pmd_releases/${PMD_VERSION}/pmd-bin-${PMD_VERSION}.zip \
    && unzip pmd-bin-${PMD_VERSION}.zip -d ${PMD_DIRECTORY}