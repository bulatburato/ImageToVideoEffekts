import tkinter as tk
from tkinter import filedialog
from PIL import Image
import cv2
import numpy as np
from moviepy.editor import concatenate_videoclips, VideoFileClip

def create_video(speed, window, filename, effects):
    img = Image.open(filename)
    height, width = img.size
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_filename = filedialog.asksaveasfilename(defaultextension=".mp4")
    video = cv2.VideoWriter(output_filename, fourcc, speed * 3, (height, width))  # Geschwindigkeit auf das Dreifache setzen

    for i in range(1, 101):
        scale = i if 'Zoom In' in effects else 101 - i
        img_resized = img if 'Flash' in effects else img.resize((int(height * scale / 100), int(width * scale / 100)))
        img_blank = Image.new('RGB', (height, width), (0, 0, 0))  # Hintergrundfarbe auf Schwarz setzen
        img_blank.paste(img_resized, (int((height - img_resized.size[0]) / 2), int((width - img_resized.size[1]) / 2)))
        frame = np.array(img_blank)

        # Effekte anwenden
        if 'Rotate' in effects:
            img_rotated = img.rotate(i * 3.6)
            frame = np.array(img_rotated)
        if 'Flash' in effects and i % 2 == 0:
            frame = np.zeros((height, width, 3), dtype=np.uint8)
        if 'LtoR' in effects:
            M = np.float32([[1, 0, i * width / 100], [0, 1, i * height / 100]])
            frame = cv2.warpAffine(frame, M, (width, height))
        if 'RtoL' in effects:
            M = np.float32([[1, 0, -i * width / 100], [0, 1, i * height / 100]])
            frame = cv2.warpAffine(frame, M, (width, height))

        video.write(frame)

    # Das Bild für 4 Sekunden ohne Effekt beibehalten
    for _ in range(4 * speed * 3):  # Geschwindigkeit auf das Dreifache setzen
        video.write(np.array(img_blank))

    video.release()

def create_video_concatenate():
    filenames = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.flv;*.mkv;*.wmv")], 
                                            title="Wählen Sie bis zu 10 Videos aus", 
                                            initialdir="/", 
                                            parent=root)

    clips = [VideoFileClip(filename) for filename in filenames]

    final_clip = concatenate_videoclips(clips, method="compose", padding=-2)

    output_filename = filedialog.asksaveasfilename(defaultextension=".mp4")
    final_clip.write_videofile(output_filename)

def create_window(title, old_window=None):
    if old_window:
        old_window.destroy()
    window = tk.Toplevel(root)
    window.title(title)
    menu = tk.Menu(window)
    window.config(menu=menu)
    filemenu = tk.Menu(menu)
    menu.add_cascade(label="Fenster", menu=filemenu)
    filemenu.add_command(label="1", command=lambda: create_window('1', window))
    filemenu.add_command(label="2", command=lambda: create_window('2', window))
    filemenu.add_command(label="3", command=lambda: create_window('3', window))
    filemenu.add_command(label="4", command=lambda: create_window('4', window))

    if title == '1':
        listbox = tk.Listbox(window)
        for i in range(1, 11):
            listbox.insert(i, str(i))
        listbox.pack()

        effects = ['Zoom In', 'Zoom Out', 'Rotate', 'Flash', 'LtoR', 'RtoL']
        effects_var = {effect: tk.BooleanVar() for effect in effects}
        for effect, var in effects_var.items():
            tk.Checkbutton(window, text=effect, variable=var).pack()

        button1 = tk.Button(window, text="Bild auswählen", command=lambda: window.filename.set(filedialog.askopenfilename()))
        button1.pack()

        window.filename = tk.StringVar(window)  # Variable zum Speichern des Dateinamens

        button2 = tk.Button(window, text="Erstellen", command=lambda: create_video(int(listbox.curselection()[0] if listbox.curselection() else tk.messagebox.showerror("Fehler", "Bitte Geschwindigkeit angeben")), window, window.filename.get(), [effect for effect, var in effects_var.items() if var.get()]))
        button2.pack()

        filemenu.add_command(label="Videoschnitt", command=create_video_concatenate)

root = tk.Tk()
root.withdraw()
create_window('1')
root.mainloop()
