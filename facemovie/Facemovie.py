'''
Created on 27 mars 2012

@author: jll
'''
import os
import sys

import cv

import Guy
from FaceParams import FaceParams

class FaceMovie(object):
    '''
    Main class of the whole application. 
    Contains the core image processing functions.
    Supports the communication layer with the end user interface.
    '''
    def __init__(self, in_folder, out_folder, face_params):
        '''
        Constructor
        '''
        self.source= in_folder # Source folder for pictures
        self.out = out_folder # Folder to save outputs
        
        self.guys = [] # List of pictures in source folder
        
        # Retrieving parameters for Face Detection
        self.face_params = face_params
        
        # Position of the center in output images 
        self.x_center = 0
        self.y_center = 0

        # minimum size needed on right of center
        self.x_af = 0
        self.y_af = 0
        
        # Needed minimum size of output image
        self.dim_x = 0
        self.dim_y = 0
        
    def list_guys(self):
        """
        Aims at populating the guys list, using the source folder as an input. 
        Guys list shall be sorted by file name alphabetical order
        """
        try:
            os.path.exists(self.source)
            os.path.isdir(self.source) # checking if folder exists
        except : # find precise exception
            print "ERROR : Source folder not found ! Exiting. . ." 
            sys.exit(0)
            
        # just listing directory. Lets be more secure later
        files = os.listdir(self.source)
        
        # loading images, create Guys and store it into guys
        for token in files :
            image = cv.LoadImage(os.path.join(self.source, token))
            guy_name = os.path.splitext(token)[0]
            a_guy = Guy.Guy(image, guy_name)
         
            # populating guys
            self.guys.append(a_guy)

    def search_faces(self):
        """
        Searches for all faces in the guys we have
        Results to be stored directly in guys
        """
        for a_guy in self.guys:
            a_guy.search_face(self.face_params)
            if a_guy.has_face(): # face(s) have been found
                print "%d faces found for %s" % (a_guy.num_faces(), a_guy.name)
            else:
                print "Warning! No face found for %s" %(a_guy.name)
    
    def normalize_faces(self, reference=0):
        """
        Creates new images, normalized by face size
        """
        if reference == 0:
            reference = self.guys[0].faces[0][0][3] # catch face size (width)
            
        for a_guy in self.guys:
            if a_guy.has_face():
                a_guy.normalize_face(reference)
    
    def find_out_dims(self):
        """
        Calculates best output image size and position depending on
        faces found in guys.
        """
        # FIXME: badly done !
        for a_guy in self.guys:
            if a_guy.has_face():
                xc = a_guy.x_center
                yc = a_guy.y_center
                inx = a_guy.in_x
                iny = a_guy.in_y
                    
                # update center
                if xc > self.x_center:
                    self.x_center = xc
                if yc > self.y_center:
                    self.y_center = yc
                # update right part
                if (inx - xc) > self.x_af:
                    self.x_af = inx - xc
                if (iny - yc) > self.y_af:
                    self.y_af = iny - yc
        
        self.dim_x = self.x_af + self.x_center
        self.dim_y = self.y_af + self.y_center
        
    def show_faces(self, mytime=1000, equalize=True):
        """
        Show all faces that have been found for the guys.
        The time for which each image will be displayed can be chosen.
        Several modes can be chosen to adapt the result.
        """
        for a_guy in self.guys:
            if a_guy.has_face():     
                out_im = a_guy.create_video_output(self.dim_x, 
                                          self.dim_y, 
                                          self.x_center, 
                                          self.y_center)
                self.out_display(out_im, a_guy.name, time=mytime)      

    def save_faces(self, out_folder, im_format="png"):
        """
        Save all faces into out_folder, in the given image format
        Debug is used to draw rectangles around found faces
        """
        for a_guy in self.guys: 
            if a_guy.has_face():
                out_im = a_guy.create_video_output(self.dim_x, 
                                          self.dim_y, 
                                          self.x_center, 
                                          self.y_center)
                self.save_result(out_im, a_guy.name, out_folder, im_format)    
                          
    def save_movie(self, out_folder, equalize=True):
        """
        Creates a movie with all faces found in the inputs.
        Guy is skipped if no face is found.
        
        TODO : No codec involved !
        TODO : Can FPS be changed?
        Resize should be done somewhere else !
        """
        filename = os.path.join(out_folder, "output.avi")
        fourcc = cv.CV_FOURCC('C', 'V', 'I', 'D')
        fps = 3 # not taken into account

        frameSize = (self.dim_x, self.dim_y)     
        my_video = cv.CreateVideoWriter(filename, 
                                      fourcc, 
                                      fps, 
                                      frameSize,
                                      1)
        ii = 0 
        for a_guy in self.guys:
            ii += 1 
            if a_guy.has_face():
                print "frame %d" %(ii) 
                out_im = a_guy.create_video_output(self.dim_x, 
                                          self.dim_y, 
                                          self.x_center, 
                                          self.y_center)         
                cv.WriteFrame(my_video, out_im)

    def number_guys(self):
        """
        Simply returns the number of guys in the current to-be movie
        """    
        return len(self.guys)
    
    def out_display(self, im, name, time=1000, im_x=640, im_y=480):
        """
        Displays the output image, for time ms.
        Setting time to 0 causes the image to remains open.
        Window name slightly changed to match output
        """
        win_name = name + " - out"
        cv.NamedWindow(win_name, cv.CV_WINDOW_NORMAL)
        cv.ResizeWindow(win_name, im_x, im_y) 
        cv.ShowImage(win_name, im)
        cv.WaitKey(time)
        cv.DestroyWindow(win_name)
        
    def save_result(self, im, name, out_folder, ext):
        """
        Saves output image to the given format (given in extension)
        """
        file_name = name + "." + ext
        out_name = os.path.join(out_folder, file_name)
        print "Saving %s" %(out_name)
        
        cv.SaveImage(out_name, im)