import eel
import desktop
import main


app_name="html"
end_point="main.html"
size=(700,600)

@eel.expose
def run(place,job,keyword):
    main.run(place,job,keyword)

    
desktop.start(app_name,end_point,size)
#desktop.start(size=size,appName=app_name,endPoint=end_point)