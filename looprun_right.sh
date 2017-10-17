for file in /Users/liangchuangu/Downloads/KITTI/07/image_3/*.png
do
  ./darknet detector test cfg/coco.data cfg/yolo.cfg yolo.weights "$file"
done