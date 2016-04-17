DIR=$1
BATCH_SIZE=$2
SUBDIR_NAME=$3
COUNTER=1

while [ `find $DIR -maxdepth 1 -type f| wc -l` -ge $BATCH_SIZE ] ; do
  NEW_DIR=$DIR/$SUBDIR_NAME${COUNTER}
  mkdir $NEW_DIR
  find $DIR -maxdepth 1 -type f | head -n $BATCH_SIZE | xargs -I {} mv {} $NEW_DIR
  let COUNTER++
done
