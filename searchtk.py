import tkinter


tcl_path = tkinter.Tcl().eval('info library')

print("TCL_LIBRARY:", tcl_path)


tk_path = tcl_path.replace("tcl", "tk")

print("TK_LIBRARY:", tk_path)
