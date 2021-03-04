from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from keras.models import load_model
import numpy as np
import cv2

# get the last index from last_index.txt to create continuous image file name
last_index = -1
with open("last_index.txt", "r") as f:
    for line in f:
        last_index = int(line)
        break


# load model
model = load_model('final_model.h5')

# init tkinter
root = Tk()
root.geometry("900x600")
root.resizable(False, False)

# init some important parameters
df_size = (450, 600)  # Size of draw frame
af_size = (450, 600)  # Size of answer frame
cv_size = (224, 224)  # Size of canvas
canvas_x = (df_size[0]-cv_size[0])//2
canvas_y = 180
tmp_image = np.zeros((28, 28))


is_held = False
digit = - 1
is_correct = None
predicted = False


# when mouse is moved
def move(event):
    if is_held and (0 <= event.x < cv_size[0] and 0 <= event.y < cv_size[1]):
        canvas.create_rectangle(event.x - 6, event.y - 6, event.x + 14, event.y + 14, fill="#ffffff", width=0)
        x = event.x // 8
        y = event.y // 8
        # 72 151 167 233 255
        tmp_image[y, x] = 255
        if y - 1 >= 0:
            tmp_image[y - 1, x] = 255
        if y + 1 < 28:
            tmp_image[y + 1, x] = 255
        if x - 1 >= 0:
            tmp_image[y, x - 1] = 255
        if x + 1 < 28:
            tmp_image[y, x + 1] = 255
        if y - 1 >= 0 and x - 1 >= 0:
            tmp_image[y - 1, x - 1] = max(72, tmp_image[y - 1, x - 1])
        if y - 1 >= 0 and x + 1 < 28:
            tmp_image[y - 1, x + 1] = max(151, tmp_image[y - 1, x + 1])
        if y + 1 < 28 and x - 1 >= 0:
            tmp_image[y + 1, x - 1] = max(167, tmp_image[y + 1, x - 1])
        if y + 1 < 28 and x + 1 < 28:
            tmp_image[y + 1, x + 1] = max(233, tmp_image[y + 1, x + 1])


# when left mouse is clicked
def left_hold(event):
    global is_held
    is_held = True


# when left mouse is released
def left_release(event):
    global is_held
    is_held = False


# clear the drawing area
def btn_clear_action():
    canvas.delete("all")
    global tmp_image, is_correct, predicted
    tmp_image = np.zeros((28, 28))
    lb_digit['text'] = "-1"
    btn_correct.configure(bg='white')
    btn_incorrect.configure(bg='white')
    cbx_correct.place_forget()
    is_correct = None
    predicted = False


# predict the number in the drawing form
def btn_predict_action():
    img = tmp_image.reshape(1, 28, 28, 1)
    img = img.astype('float32')
    img = img / 255.0
    digits = model.predict_classes(img)
    global digit, predicted
    predicted = True
    digit = digits[0]
    lb_digit['text'] = str(digit)


# check if digit is correct
def btn_correct_action():
    global is_correct, predicted
    if not predicted:
        messagebox.showerror("Error", "You have to predict first!")
    else:
        btn_correct.configure(bg='green')
        btn_incorrect.configure(bg='white')
        cbx_correct.place_forget()
        is_correct = True


# check if digit is not correct
def btn_incorrect_action():
    global is_correct, predicted
    if not predicted:
        messagebox.showerror("Error", "You have to predict first!")
    else:
        btn_correct.configure(bg='white')
        btn_incorrect.configure(bg='red')
        cbx_correct.place(x=350, y=410)
        is_correct = False


# save the image to training set
def btn_save_action():
    global is_correct, last_index
    if is_correct is None:
        messagebox.showerror("Error", "You have to choose correct or incorrect first!")
        return
    if not is_correct and not cbx_correct.get():
        messagebox.showerror("Error", "Correct the digit first to save!")
        return
    if is_correct:
        correct_answer = digit
    else:
        correct_answer = int(cbx_correct.get())
    filename = "training_set/" + str(correct_answer) + "_" + str(last_index).zfill(6) + ".png"
    cv2.imwrite(filename, tmp_image)
    last_index += 1
    messagebox.showinfo("Information", "Save successfully!")
    btn_clear_action()


# On draw frame
draw_frame = Frame(root, bg="blue", width=df_size[0], height=df_size[1])
draw_frame.place(x=0, y=0)
draw_frame.pack_propagate(False)


lb_draw = Label(draw_frame, text="Draw your number: ", font=("Times", 24, "italic bold"), bg="blue")
lb_draw.place(x=100, y=50)


canvas = Canvas(draw_frame, width=224, height=224, bg="black")
canvas.bind("<Motion>", move)
canvas.bind("<Button-1>", left_hold)
canvas.bind("<ButtonRelease-1>", left_release)
canvas.place(x=canvas_x, y=canvas_y)


btn_clear = Button(draw_frame, text='Clear', font=("Times", 16, "bold"), command=lambda: btn_clear_action())
btn_clear.place(x=100, y=500)

btn_predict = Button(draw_frame, text='Predict', font=("Times", 16, "bold"), command=lambda: btn_predict_action())
btn_predict.place(x=270, y=500)

# On answer frame
answer_frame = Frame(root, bg="dark gray", width=af_size[0], height=af_size[1])
answer_frame.place(x=450, y=0)
answer_frame.pack_propagate(False)

lb_answer = Label(answer_frame, text="Answer: ", font=("Times", 24, "italic bold"), bg="dark gray", fg="yellow")
lb_answer.place(x=100, y=50)

correct_digit = 0
lb_ynb = Label(answer_frame, text="Your number is: ", font=("Times", 16, "bold"), bg="dark gray")
lb_ynb.place(x=150, y=150)

lb_digit = Label(answer_frame, text="-1", font=("Times", 100, "bold"), bg="dark gray", fg="yellow")
lb_digit.place(x=190, y=200)

btn_correct = Button(answer_frame, text="Correct", font=("Times", 16, "bold"), command=lambda: btn_correct_action())
btn_correct.place(x=100, y=400)

btn_incorrect = Button(answer_frame, text="Incorrect", font=("Times", 16, "bold"), command=lambda: btn_incorrect_action())
btn_incorrect.place(x=250, y=400)

cbx_correct = ttk.Combobox(answer_frame, values=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], width=5, height=10)

btn_save = Button(answer_frame, text="Save to training dataset", font=("Times", 16, "bold"), command=lambda: btn_save_action())
btn_save.place(x=110, y=500)

root.mainloop()

# update new last index into last_index.txt file
with open("last_index.txt", "w") as f:
    f.write(str(last_index))
