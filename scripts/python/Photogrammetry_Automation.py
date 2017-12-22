from abc import ABCMeta, abstractmethod

class Photogrammetry_Controller:
    __metaclass__ = ABCMeta

    @abstractmethod
    def CheckPrerequisites(self):
          return "JSON"
        
    @abstractmethod
    def Mark_Step_Running(self):
          return "Marked"

    @abstractmethod
    def Execute_step(self):
          return "Executed"
        
    @abstractmethod
    def Check_Accuracy(self):
          return "Checked"
    
    @abstractmethod
    def Export_Output(self):
          return "Exported"
        
    @abstractmethod
    def Mark_Step_Complete(self):
          return "Marked"
        
class Inspect_Image(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Inspect_Image, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Inspect_Image, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(Inspect_Image, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(Inspect_Image, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Inspect_Image, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Inspect_Image, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")

class Align_Photos(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Align_Photos, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Align_Photos, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "Align_Photos returned")
    
    def Execute_step(self):
        s = super(Align_Photos, self).Execute_step()
        print s
        return "%s - %s" % (s, "Align_Photos returned")
    
    def Check_Accuracy(self):
        s = super(Align_Photos, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Align_Photos, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Align_Photos, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")   

class Build_Sparse_Point_Cloud(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Build_Sparse_Point_Cloud, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Build_Sparse_Point_Cloud, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(Build_Sparse_Point_Cloud, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(Build_Sparse_Point_Cloud, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Build_Sparse_Point_Cloud, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Build_Sparse_Point_Cloud, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")    

class  GCP_Based_Georeferencing(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(GCP_Based_Georeferencing, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(GCP_Based_Georeferencing, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(GCP_Based_Georeferencing, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(GCP_Based_Georeferencing, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(GCP_Based_Georeferencing, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(GCP_Based_Georeferencing, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")    

class  Optimize_Camera(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Optimize_Camera, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Optimize_Camera, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(Optimize_Camera, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(Optimize_Camera, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Optimize_Camera, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Optimize_Camera, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")    

class  Build_Dense_Point_Cloud(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Build_Dense_Point_Cloud, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Build_Dense_Point_Cloud, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(Build_Dense_Point_Cloud, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(Build_Dense_Point_Cloud, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Build_Dense_Point_Cloud, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Build_Dense_Point_Cloud, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")    

class  Build_DEM(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Build_Mesh, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Build_Mesh, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(Build_Mesh, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(Build_Mesh, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Build_Mesh, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Build_Mesh, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")

class  Build_Orthomosaic(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Build_Orthomosaic, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Build_Orthomosaic, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(Build_Orthomosaic, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(Build_Orthomosaic, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Build_Orthomosaic, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Build_Orthomosaic, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")    
    
class  Build_Mesh(Photogrammetry_Controller):
    def CheckPrerequisites(self):
        s = super(Build_DEM, self).CheckPrerequisites()
        print s
        return "%s - %s" % (s, "returned")
    
    def Mark_Step_Running(self):
        s = super(Build_DEM, self).Mark_Step_Running()
        print s
        return "%s - %s" % (s, "returned")
    
    def Execute_step(self):
        s = super(Build_DEM, self).Execute_step()
        print s
        return "%s - %s" % (s, "returned")
    
    def Check_Accuracy(self):
        s = super(Build_DEM, self).Check_Accuracy()
        print s
        return "%s - %s" % (s, "returned")
    
    def Export_Output(self):
        s = super(Build_DEM, self).Export_Output()
        print s
        return "%s - %s" % (s, "returned")

    def Mark_Step_Complete(self):
        s = super(Build_DEM, self).Mark_Step_Complete()
        print s
        return "%s - %s" % (s, "returned")

c=Inspect_Image()
d=Align_Photos()
c.CheckPrerequisites()
c.Mark_Step_Running()
c.Execute_step()
c.Check_Accuracy()
c.Export_Output()
c.Mark_Step_Complete()
d.CheckPrerequisites()
d.Mark_Step_Running()
d.Execute_step()
d.Check_Accuracy()
d.Export_Output()
d.Mark_Step_Complete()