from tkinter import *

root = None
sms_code = None


def check_sms_code(content):
    global sms_code
    print(content)
    sms_code = content
    if (content.isdigit() and len(content) <= 6) or len(content) == 0:
        return True
    return False


def get_sms_code():
    return sms_code


def destroy():
    if isinstance(root, Tk):
        print('submit then destroy')
        root.destroy()
    # win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))


def input_sms_code(submit_callback):
    global root
    global value
    root = Tk()
    root.title('请输入短信验证码')

    Label(root, text='短信验证码 :').grid(row=0, column=0)
    value = StringVar()
    cmd = root.register(check_sms_code)
    editor = Entry(root, width=10, textvariable=value, validate='key', validatecommand=(cmd, '%P'))
    editor.grid(row=0, column=1, padx=10, pady=5)
    root.geometry('400x200')

    Button(root, text='确定', width=6, highlightbackground='#55CEAC', command=submit_callback) \
        .grid(row=0, column=2, padx=10, pady=5)

    root.mainloop()
