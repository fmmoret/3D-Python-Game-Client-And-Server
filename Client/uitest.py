"""Demos clicking on screen elements vs clicking on the environment."""

from cefpython3 import cefpython

import math
import os
import sys


from panda3d.core import loadPrcFileData
loadPrcFileData("", "Panda3D example -- Transparent window")
loadPrcFileData("", "fullscreen 0")
loadPrcFileData("", "win-size 1024 768")
loadPrcFileData("", "textures-power-2 none")

import direct.directbase.DirectStart
from panda3d.core import CardMaker
from panda3d.core import PNMImage, Point3, Texture, TransparencyAttrib, VBase4
# For 3d picker
from panda3d.core import CollisionHandlerQueue, CollisionNode, CollisionRay, CollisionTraverser, GeomNode

from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence

base.setFrameRateMeter(True)


settings = {
        "log_severity": cefpython.LOGSEVERITY_ERROR, # LOGSEVERITY_VERBOSE
        #"log_file": GetApplicationPath("debug.log"), # Set to "" to disable.
        #"release_dcheck_enabled": True, # Enable only when debugging.
        # This directories must be set on Linux
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess")
    }


html = """<html>
<head>
<!-- Bootstrap - Now making generic looking UI too! -->
<link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
<link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css">
<!-- Override premade style. CSS background has to be transparent for the texture to be transparent. -->
<style>
body {background-color: rgba(0,0,0,0.0);}
.vbtm {
    display: inline-block;
    vertical-align: bottom;
    float: none;
}
</style>
</head>
<body>
<script language="JavaScript">
$('.pull-down').each(function() {
    $(this).css('margin-top', $(this).parent().height()-$(this).height())
});
function setFrameCount(counter){
    document.getElementById("framecount").innerHTML=counter;
};
function setOtherMessage(text){
    document.getElementById("othermessage").innerHTML=text;
};
</script>
    <row>
        <div class="col-md-6">
            <div class="well"><h2>""" + sys.version + """</h2></div>
        </div>
    </row>
    <row>
        <div class="col-md-6 pull-down">
            <div class="well"><h3>Message: <small><script>
                document.write(window.sometext);
                </script></small></h3></div>
        </div>
        <div class="col-md-6 pull-down">
            <div class="well"><h3>Number of Frames: <small><span id="framecount"></span></small></h3></div>
        </div>
        <div class="col-md-6 pull-down">
            <div class="well"><h3>Other Message: <small><span id="othermessage"></span></small></h3></div>
        </div>
    </row>
<br />
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
<script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
</body>
</html>"""

class ClientHandler(object):
    """A client handler is required for the browser to do built-in callbacks back into the application."""
    browser = None
    texture = None

    def __init__(self, browser, texture):
        self.browser = browser
        self.texture = texture

    def OnPaint(self, browser, paintElementType, dirtyRects, buffer, width, height):
        img = self.texture.modifyRamImage()
        if paintElementType == cefpython.PET_POPUP:
            print("width=%s, height=%s" % (width, height))
        elif paintElementType == cefpython.PET_VIEW:
            img.setData(buffer.GetString(mode="rgba", origin="bottom-left"))
        else:
            raise Exception("Unknown paintElementType: %s" % paintElementType)

    def GetViewRect(self, browser, rect):
        width = self.texture.getXSize()
        height = self.texture.getYSize()
        rect.append(0)
        rect.append(0)
        rect.append(width)
        rect.append(height)
        return True

    def GetScreenPoint(self, browser, viewX, viewY, screenCoordinates):
        print("GetScreenPoint()", browser, viewX, viewY, screenCoordinates)
        return False

    def OnLoadEnd(self, browser, frame, httpStatusCode):
        return
        self._saveImage()

    def OnLoadError(self, browser, frame, errorCode, errorText, failedURL):
        print("load error", browser, frame, errorCode, errorText, failedURL)

def messageLoop(task):
    cefpython.MessageLoopWork()
    """Call a specific javascript function and pass any parameters to it."""
    browser.GetMainFrame().CallFunction("setFrameCount", task.frame)

    return task.cont


def setVariable(name, value):
    """Sets a javascript value in the main frame"""
    jsBindings.SetProperty(name, value)


def setBrowserSize(window=None):
    """Set the off screen browser to the same resolution of the panda window.
    Best I can find is creating a new texture on resize.
    """
    texture = make_texture()
    nodePath.setTexture(texture)
    handler.texture = texture
    browser.WasResized()


def make_texture():
    texture = Texture()
    texture.setCompression(Texture.CMOff)
    texture.setComponentType(Texture.TUnsignedByte)
    texture.setFormat(Texture.FRgba4)
    texture.setXSize(base.win.getXSize())
    texture.setYSize(base.win.getYSize())
    return texture



cefpython.g_debug = True
cefpython.Initialize(settings)


windowHandle = base.win.getWindowHandle().getIntHandle()
windowInfo = cefpython.WindowInfo()
print windowInfo

#You can pass 0 to parentWindowHandle, but then some things like context menus and plugins may not display correctly.
windowInfo.SetAsOffscreen(windowHandle)
#windowInfo.SetAsOffscreen(0)
windowInfo.SetTransparentPainting(True)
browserSettings = {}

# Using non about:blank in constructor results in error before render handler callback is set.
# Either set it before/during construction, or set it after then call LoadURL after it is set.
browser = cefpython.CreateBrowserSync(
                windowInfo, browserSettings,
                navigateUrl="http://www.panda3d.org")
browser.SendFocusEvent(True)
handler = ClientHandler(browser, make_texture())
browser.SetClientHandler(handler)

cardMaker = CardMaker("browser2d")
cardMaker.setFrameFullscreenQuad()
node = cardMaker.generate()
#For UI attach to render2d
nodePath = render2d.attachNewNode(node)
nodePath.setTransparency(TransparencyAttrib.MAlpha)
nodePath.setTexture(handler.texture)

#setBrowserSize()

base.accept("window-event", setBrowserSize)


# Example of one kind of call back
def on_load_end(*args, **kwargs):
    print "I loaded!"


browser.SetClientCallback("OnLoadEnd", on_load_end)

browser.GetMainFrame().LoadString(html, "http://fake")

'''IMPORTANT: there is a bug in CEF 3 that causes js bindings to be removed when LoadUrl() is called (see http://www.magpcss.org/ceforum/viewtopic.php?f=6&t=11009). A temporary fix to this bug is to do the navigation through javascript by calling: GetMainFrame().ExecuteJavascript('window.location="http://google.com/"').'''
#browser.GetMainFrame().ExecuteJavascript('window.location="http://www.google.com"')
#browser.GetMainFrame().LoadUrl("http://wwww.panda3d.org")


"""Sets up bindings to access javascript variables and functions. Also is used for calling back into python."""
jsBindings = cefpython.JavascriptBindings(bindToFrames=False, bindToPopups=True)
jsBindings.SetProperty("sometext", "A message from python land! Hello!")
browser.SetJavascriptBindings(jsBindings)

taskMgr.add(messageLoop, "CefMessageLoop")


"""Set up 'generic' picker from Clicking on 3D objects manual"""
myTraverser = CollisionTraverser('mousePicker')
base.cTrav = myTraverser
myHandler = CollisionHandlerQueue()

pickerNode = CollisionNode('mouseRay')
pickerNP = camera.attachNewNode(pickerNode)
pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
pickerRay = CollisionRay()
pickerNode.addSolid(pickerRay)
myTraverser.addCollider(pickerNP, myHandler)


def click_object():
    # First we check that the mouse is not outside the screen.
    if base.mouseWatcherNode.hasMouse():
        # This gives up the screen coordinates of the mouse.
        mpos = base.mouseWatcherNode.getMouse()
        # This makes the ray's origin the camera and makes the ray point
        # to the screen coordinates of the mouse.
        try:
            pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            myTraverser.traverse(render)
            # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
            if myHandler.getNumEntries() > 0:
                # This is so we get the closest object
                myHandler.sortEntries()
                pickedObj = myHandler.getEntry(0).getIntoNodePath()
                if not pickedObj.isEmpty():
                    handlePickedObject(pickedObj)
        except:
            print 'AVOIDED CRASH'


def handlePickedObject(picked_object):
    browser.GetMainFrame().CallFunction("setOtherMessage", "You poked " + str(picked_object))
"""End set up 'generic' picker from Clicking on 3D objects manual"""


def onMouseDown():
    '''This logic is set up for an ui where the mouse will be interacting with
    both ui elements and in world elements, such as an rts, tbs, or simulation
    game. This requires checking if the pixel the mouse clicked on is ui or
    not.
    We do this by checking the alpha level of the ui texture. If there is
    no alpha we hand off to the other parts of the mouse ui logic. If there
    is alpha the mouse click is passed to the browser instead.
    It is advised to create another mouse click event that is fired when
    alpha = 0 and have the additional logic listen for that. Otherwise
    anything listening to mouse1 and mouse1-up will fire reguardless of
    the position of the mouse.'''

    if base.win.has_pointer(0):
        x = int(base.win.get_pointer(0).get_x())
        y = int(base.win.get_pointer(0).get_y())
        '''# This is probably a more memory efficent, but does not work
        peek = handler.texture.peek()
        color = VBase4(1, 0, 1, 0)
        peek.lookup(color, int(x), int(y))
        print color, x, y'''
        # So this way instead!
        image = PNMImage()
        handler.texture.store(image)
        nodePath.setTexture(handler.texture)
        try:
            if image.get_alpha(x, y):
                browser.SendMouseClickEvent(x, y, cefpython.MOUSEBUTTON_LEFT,
                    mouseUp=False, clickCount=1)
            else:
                print("Screen picking logic here!")
                click_object()
            image.clear()
        except:
            print "AVOIDED CRASH"


def onMouseUp():
    '''You may wish to pass all mouse-up events to both the browser
    and the game logic, depending on your needs.'''
    if base.win.has_pointer(0):
        x = int(base.win.get_pointer(0).get_x())
        y = int(base.win.get_pointer(0).get_y())
        '''# This is probably a more memory efficent, but does not work
        peek = handler.texture.peek()
        color = VBase4(1, 0, 1, 0)
        peek.lookup(color, int(x), int(y))
        print color, x, y'''

        image = PNMImage()
        handler.texture.store(image)
        nodePath.setTexture(handler.texture)
        try:
            if image.get_alpha(x, y):
                browser.SendMouseClickEvent(x, y, cefpython.MOUSEBUTTON_LEFT,
                    mouseUp=True, clickCount=1)
            else:
                print("Screen picking logic here!")
            image.clear()
        except:
            print "AVOIDED CRASH 2"


base.accept("mouse1", onMouseDown)
base.accept("mouse1-up", onMouseUp)
'''print 'messageloop'
from threading import Thread
def runthis():
    cefpython.MessageLoop()
Thread(target=runthis).start()
print 'called message loop'''
