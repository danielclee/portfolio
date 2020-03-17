import tkinter
import tkinter.ttk as ttk
import time

MAX = 100

def loop_function():
    root = tkinter.Tk()
    root.geometry('{}x{}'.format(400, 100))
    root.title("Hello World")
    progress_var = tkinter.DoubleVar()
    theLabel = tkinter.Label(root, text="Download progress")
    theLabel.pack()
    progressbar = ttk.Progressbar(root, variable=progress_var, maximum=MAX)
    progressbar.pack(fill=tkinter.X, expand=1)
    progressbar.pack()
    k = 0
    while k <= MAX:
        time.sleep(1.0)
        progress_var.set(k)
        k += 1
        theLabel['text'] = "Hello World : " + str(k)
        print(k)
        root.update_idletasks()
    progressbar = None
    root = None
    ##root.after(100, loop_function)


def main():
    print("Starting test")
    loop_function()
    print("Test ended")


if __name__ == "__main__":
    main()
    
