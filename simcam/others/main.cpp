//g++ -std=c++11 `pkg-config --cflags --libs opencv` main.cpp -o main
#include "opencv2/core.hpp"
#include <opencv2/core/utility.hpp>
#include "opencv2/imgproc.hpp"
#include "opencv2/video/background_segm.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/highgui.hpp"
#include <stdio.h>
#include <string>
#include <sstream>
#include <iostream>
#include <time.h>
#include <vector>

using namespace std;
using namespace cv;

static void help()
{
  printf("\nDo background segmentation, especially demonstrating the use of cvUpdateBGStatModel().\n"
	 "Learns the background at the start and then segments.\n"
	 "Learning is togged by the space key. Will read from file or camera\n"
	 "Usage: \n"
	 "			./bgfg_segm [--camera]=<use camera, if this key is present>, [--file_name]=<path to movie file> \n\n");
}

const char* keys =
  {
    "{c  camera   |         | use camera or not}"
    "{m  method   |mog2     | method (knn or mog2) }"
    "{s  smooth   |         | smooth the mask }"
    "{fn file_name|../data/tree.avi | movie file        }"
  };

//this is a sample for foreground detection functions

int timeToResendAlarm = 30;
int areaAlarm = 2000;

bool IntruderDetected = false;

bool alarmSystem(Mat& blob, Mat& img, string currTime);
int currTime_Seconds();
int FiveSecCheck();
string format_time();
void format_bash(string& source, string const& find, string const& replace);

int main(int argc, const char** argv)
{
  help();

  CommandLineParser parser(argc, argv, keys);
  bool useCamera = parser.has("camera");
  bool smoothMask = parser.has("smooth");
  string file = parser.get<string>("file_name");
  string method = parser.get<string>("method");
  VideoCapture cap(0);
  bool update_bg_model = true;

  if(useCamera){cap.open(0);}
  else{cap.open(file.c_str());}

  parser.printMessage();

  if(!cap.isOpened() ){
    printf("can not open camera or video file\n");
    return -1;
  }

  Ptr<BackgroundSubtractor> bg_model = method == "knn" ?
    createBackgroundSubtractorKNN().dynamicCast<BackgroundSubtractor>() :
    createBackgroundSubtractorMOG2().dynamicCast<BackgroundSubtractor>();
    
  Mat img0, img, blob, fgimg;

  unsigned int alarmSeconds = 30;
  unsigned int triggerTime = 0;
  unsigned int SecCount = 0;
  
  unsigned int sendImageDelay = 2;
  unsigned int delayTime = currTime_Seconds() + 1;
    
  while(1){
    
    cap >> img0;

    if( img0.empty()) {break;}

    resize(img0, img, Size(640, 480));

    if( fgimg.empty() ) {fgimg.create(img.size(), img.type());}
      
    bg_model->apply(img, blob, update_bg_model ? -1 : 0);
    
    if(smoothMask){
      GaussianBlur(blob, blob, Size(11, 11), 3.5, 3.5);
    }
    
    threshold(blob, blob, 50, 255, THRESH_BINARY);

    fgimg = Scalar::all(0);
    img.copyTo(fgimg, blob);
    
    Mat bgimg;
    bg_model->getBackgroundImage(bgimg);

    string currTime = format_time();

    putText(img, currTime, Point(1,470), 1,1, Scalar(0,255,0), 2);
    int currSec = currTime_Seconds();

    if(delayTime < currSec){
      if (currSec >= triggerTime){ // check if time to resend image has come
	if (alarmSystem(blob, img, currTime)){ // if alarm triggered
	  SecCount++;
	  if(SecCount > 2){
	      
	    string imgName = "/home/pi/Documents/SecurityImages/"+currTime+".jpg";
	    string bashCommand = imgName;
	      
	    format_bash(bashCommand, " ", "\\ ");
	    format_bash(bashCommand, ":", "\\:");
	    string sendImg = "mpack -s ALERT "+bashCommand+" fwcctv1911@gmail.com";
	      
	    triggerTime = currSec + alarmSeconds; // time till next img

	    imwrite(imgName, img);	      
	    system(sendImg.c_str());
	    
	    SecCount=0;
	  }
	}
      }
    }
    
    imshow("image", img);
    imshow("blob", blob);
      
    char k = (char)waitKey(200);

    if( k == 'q' ) {break;}
    if( k == ' ' ){
      update_bg_model = !update_bg_model;
      if(update_bg_model) {printf("Background update is on\n");}
      else                {printf("Background update is off\n");}
    }
  }
  
  return 0;
}

bool alarmSystem(Mat& blob, Mat& img, string currTime){
  
  vector<Vec4i> hierarchy;
  vector< vector<Point> > contours;
  vector< vector<Point> > contourFinal;
  
  findContours(blob, contours, hierarchy, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE);
  
  for (int i = 0; i < contours.size(); i++){
    double area = contourArea(contours[i], false);
    if (area > areaAlarm){
      // cout << area << endl;
      // putText(img, "INTRUDER DETECTED", Point(400,470), 1,1, Scalar(0,0,255), 2); 
      return true;
    }
  }
  return false;
}

int currTime_Seconds(){
  time_t timer;
  struct tm timeValues = {0};
  long long int seconds;

  timeValues.tm_hour = 0;   timeValues.tm_min = 0; timeValues.tm_sec = 0;
  timeValues.tm_year = 116; timeValues.tm_mon = 0; timeValues.tm_mday = 1;

  time(&timer);  /* get current time; same as: timer = time(NULL)  */
  
  seconds = difftime(timer,mktime(&timeValues));

  return seconds;
}

string format_time(){
  
  time_t rawtime;
  time(&rawtime);

  string currTime = ctime(&rawtime);
  currTime.pop_back();                 // remove extra character at the end

  for (int i = 0; i < currTime.length(); i++){
    if (currTime.at(i) == ' ' && currTime.at(i+1) == ' '){
      currTime.erase(i, 1);
    }
  }
  
  return currTime;  
}

void format_bash(string& source, string const& find, string const& replace){

  for (string::size_type i = 0; (i = source.find(find, i)) != string::npos;){
    source.replace(i, find.length(), replace);
    i += replace.length();
  }
  
}
