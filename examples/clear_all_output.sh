FOLDER=example_ainalysis
if [ -d "$FOLDER" ]; then
    rm -r "$FOLDER"
fi

FOLDER=my_first_ainalysis
if [ -d "$FOLDER" ]; then
    rm -r "$FOLDER"
fi

FOLDER=my_second_ainalysis
if [ -d "$FOLDER" ]; then
    rm -r "$FOLDER"
fi

FOLDER=my_updated_first_ainalysis
if [ -d "$FOLDER" ]; then
    rm -r "$FOLDER"
fi

FOLDER=my_updated_first_ainalysis_09b
if [ -d "$FOLDER" ]; then
    rm -r "$FOLDER"
fi

FILE=phenoai_server.log
if [ -f "$FILE" ]; then
    rm -r "$FILE"
fi

FILE=loggertest.out
if [ -f "$FILE" ]; then
    rm -r "$FILE"
fi