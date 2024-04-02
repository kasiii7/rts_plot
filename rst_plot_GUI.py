import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import *
from tkinter import filedialog

# Script for plotting Shear Velocity Depth Profiles (SVDP) from output .rst files from Seis Imager
# THIS CODE CAN TAKE EITHER OLD OR NEW RST FILES
# 
# By Nikolas Midttun
# April 2023
# 
# The RST files are not neat (include multiple stacked tables of different dimensions with no headers)
# The beginning of this script opens a dialog window where you specify the input file, output filename, etc.
# Then the script digests the RST file in an automated way that should accomodate .rst files of all shapes.
# Below that is code that plots the SVDP. 

#################### Parameters you might wanna change #################################

# Set font and fontsize for various elements in the plot
plt.rcParams['font.family'] = 'Frutiger LT Pro'
plt.rcParams['font.serif'] = ['55 Roman']
plt.rcParams['font.size'] = 12

point_alpha=1 # this is the transparency of the points on the SVDP (0=transparent, 1=opaque)
figure_dim = [5,6] # ouput figure dimensions in inches [height, width] 

#########################################################################################




### Create a gui and get the user's inputs ###

# Create the main window
root = Tk(screenName='RST to SVPD plotter 9000')
root.geometry("1800x400")

# initialize variables with default values
input_file = 'J:\division\school_seismic_safety'
output_file_name = 'output'
output_file_ext = '.pdf'
old_new = 'Please choose...'

# Define the function to handle the submit button
def submit():
    global input_file, output_file_name, output_file_ext, old_new
    output_file_name = output_file_name_entry.get()
    output_file_ext = output_file_ext_menu.get()
    old_new = old_new_menu.get()
    root.destroy()

# Create the input file location browse button
input_file_label = Label(root, text="Select the input .rst file:")
input_file_label.pack(pady=2)

input_frame = Frame(root)
input_frame.pack()

input_file_button = Button(input_frame, text="Browse", command=lambda: update_input_file_textbox())
input_file_button.pack(side=LEFT, padx=5)

input_file_textbox = Text(input_frame, height=1, width=200)
input_file_textbox.pack(side=LEFT)

def update_input_file_textbox():
    global input_file
    input_file = filedialog.askopenfilename(title="Select Input File")
    input_file_textbox.delete(1.0, END)
    input_file_textbox.insert(END, input_file)

# Create old vs new rst file dropdown menu
old_new_label = Label(root, text="Is this a new or old .RST file?")
old_new_label.pack(pady=2)
old_new_options = ['Please choose...', 'new', 'old']
old_new_menu = StringVar()
old_new_menu.set(old_new_options[0])
old_new_dropdown = OptionMenu(root, old_new_menu, *old_new_options)
old_new_dropdown.pack(pady=5)

# Create the output filename entry textbox
output_file_name_label = Label(root, text="Name the output file (no extension here):")
output_file_name_label.pack(pady=2)
output_file_name_entry = Entry(root)
output_file_name_entry.pack(pady=5)

# Create the output file extension dropdown menu
output_file_ext_label = Label(root, text="Select the output file extension:")
output_file_ext_label.pack(pady=2)
output_file_ext_options = ['.pdf', '.png', '.jpg', '.svg']
output_file_ext_menu = StringVar()
output_file_ext_menu.set(output_file_ext_options[0])
output_file_ext_dropdown = OptionMenu(root, output_file_ext_menu, *output_file_ext_options)
output_file_ext_dropdown.pack(pady=5)

# Create the submit button
submit_button = Button(root, text="Submit", command=submit)
submit_button.pack(pady=30)

# Start the main loop
root.mainloop()

directory, input_file = os.path.split(input_file)
os.chdir(directory) # Directory where script will look for input_file file and save output plot
output_file_name = output_file_name + output_file_ext # ouput file name with extension




# Depending on whether the user says the input file is Old or New (in the old_new variable) one of the two alternative scripts are run below:


if old_new=='new': ###################################### CODE FOR NEW RST FILES #####################################################

    temp_filename='temp_data_delete_me.txt' # name of temporary file that gets automatically deleted at the end of this script

    ####### Import and sort out the .rst file #######

    # Open the input_file file in UTF-16 LE encoding
    with open(input_file, 'r', encoding='utf-16-le') as infile:
        # Read the contents of the input_file file
        contents = infile.read()

    # Remove the BOM if it exists
    if contents.startswith('\ufeff'):
        contents = contents[1:]

    # Open the output file in UTF-8 encoding
    with open(temp_filename, 'w', encoding='utf-8') as outfile:
        # Write the contents to the output file in UTF-8 encoding
        outfile.write(contents)

    # Each separate table in the .rst file begins with a single integer that tells you how tall that table (or block, as I'm calling them) will be.
    # First we compile the integer row counts in the list rows_in_blocks.
    rows_in_blocks = []
    with open(temp_filename, "r") as f:
        for line in f:
            try:
                num = int(line.lstrip().rstrip())  # This line tries to convert each row into a single integer, and only keeps the row if it succeeds
                rows_in_blocks.append(num)
            except ValueError:  # if the row isn't an integer, it passes the row
                pass
    del rows_in_blocks[-1]
    rows_in_blocks[-1] = 2*rows_in_blocks[-1]-1 # Double the last element and subtract 1, since we need to apparently (it's just how the data are tabulated)


    # By adding 1 to the row indices of the integers extracted above, we get the starting row of each block
    row_idx = []
    with open(temp_filename, "r") as f: # extracting the row index of each integer line in the .rst file
        for i, line in enumerate(f):
            line = line.strip()
            if line.isdigit():
                row_idx.append(i)
    start_idx = [x + 1 for x in row_idx] # ading 1 to each element to get the 


    # Remove troublesome index rows that had zero for the block length
    no_zeros = [t for t in zip(start_idx, rows_in_blocks) if 0 not in t]
    start_idx, rows_in_blocks = zip(*no_zeros)

    # Now that we know the length of each block in the .rst file, and their starting rows, we can import the blocks and sort them into named variables
    blocks = []
    for i in range(len(start_idx)):
        blocks.append(np.genfromtxt(temp_filename, delimiter=' ', dtype=None, encoding='utf-8', skip_header=start_idx[i], max_rows=rows_in_blocks[i]))
    block1 = blocks[0] # 2D list with 6 columns: Vel_Meas Vel_Model Freq Coh unknown unknown
    block4 = blocks[2] # 2D list with 2 columns: Depth Modeled_velocity

    vel_meas = [row[0] for row in block1]
    vel_model = [row[1] for row in block1]
    freq = [row[2] for row in block1]

    # to calculate the depth for the dispersion curve velocities, you divide the velocity (m/s) by the frequency (1/s) to get depth (m)
    depth_meas = []
    for i in range(len(vel_meas)):
        depth_meas.append((vel_meas[i]/freq[i])/3)

    depth_model = []
    for i in range(len(vel_model)):
        depth_model.append((vel_model[i]/freq[i])/3)
    
    # Delete the temporary data file that we created at the beginning
    os.remove(temp_filename)

elif old_new=='old': ####################################### CODE FOR OLD RST FILES #######################################

    filename = input_file

    ####### Import and sort out the .rst file #######

    # Each separate table in the .rst file begins with a single integer that tells you how tall that table (or block, as I'm calling them) will be.
    # First we compile these block heights in a list called rows_in_blocks.
    rows_in_blocks = []
    with open(filename, "r") as f:
        for line in f:
            try:
                num = int(line.strip()) # This line tries to convert each row into a single integer, and only keeps the row if it succeeds
                rows_in_blocks.append(num)
            except ValueError: # if the row isn't an integer, it passes the row
                pass
    rows_in_blocks[-1] = 2*rows_in_blocks[-1]-1 # Double the last element and subtract 1, since we need to apparently (it's just how the data are tabulated)

    # By adding 1 to the row indices of the integers extracted above, we get the starting row of each block
    row_idx = []
    with open(filename, "r") as f: # extracting the row index of each integer line in the .rst file
        for i, line in enumerate(f):
            line = line.strip()
            if line.isdigit():
                row_idx.append(i)
    start_idx = [x + 1 for x in row_idx] # ading 1 to each element to get the 
    end_idx = start_idx + rows_in_blocks # adding the number of rows in each block to the start_idx to get the end_idx

    # Remove troublesome index rows that had zero for the block length
    no_zeros = [t for t in zip(start_idx, end_idx, rows_in_blocks) if 0 not in t]
    start_idx, end_idx, rows_in_blocks = zip(*no_zeros)

    # Now that we know the length of each block in the .rst file, and their starting rows, we can import the blocks and sort them into named variables
    blocks = []
    for i in range(len(start_idx)):
        blocks.append(np.genfromtxt(filename, delimiter=' ', dtype=None, encoding='utf-8', skip_header=start_idx[i], max_rows=rows_in_blocks[i]))
    block1 = blocks[0] # 4 columns: Vel_Meas	Vel_Model	Freq	Coh
    block2 = blocks[1] # not sure what this block does
    block4 = blocks[3] # 2 columns: Depth   Modeled_velocity

    vel_meas = block1[:,0]
    vel_model = block1[:,1]
    freq = [row[2] for row in block1]

    # to calculate the depth for the dispersion curve velocities, you divide the velocity (m/s) by the frequency (1/s) to get depth (m)
    depth_meas = []
    for row in block1:
        depth_meas.append((row[0]/row[2])/3)

    depth_model = []
    for row in block1:
        depth_model.append((row[0]/row[2])/3)

else:  # Outputs an error in case the user forgets to enter whether the RST is old or new. 
    print('Error: You must select whether the input file is an old or new RST file!!!! Try again.')

############# Plotting the SVDP ##############

fig1, svdp = plt.subplots(1,1,figsize=figure_dim)

# add a background grid
svdp.grid(color='gainsboro', linestyle='-', linewidth=0.5)

# plot the Vs data ###### THIS IS WHERE YOU CAN CHANGE THE SYMBOLOGY OF THE PLOT ############
plt.plot(vel_meas,depth_meas, color='cornflowerblue', marker='o', ms=4, alpha=point_alpha, label='Measured dispersion \ncurve picks', linestyle='none') # Measured velocity picks

if not vel_model[0]==0: # only plots the modeled picks if there are any (if the SVDP is based off the initial model, then no modeled picks are made)
    plt.plot(vel_model,depth_model, color='black', marker='o', ms=4, alpha=point_alpha, label='Modeled dispersion \ncurve picks', linestyle='none') # Modeled velocity picks

plt.plot(block4[:,1],block4[:,0], color='red', linewidth=1.5, label='Shear velocity \ndepth profile') # The stairstepped velocity model

svdp.invert_yaxis() # reverse the depth axis (down should be deeper)

svdp.set_xlim(left=0, right=max([vs[1] for vs in block4 if vs[0] < 35])+50) # make sure the x axis begins at zero
svdp.set_ylim(top=0, bottom=35) # make sure the y axis begins at  zero and cuts off at 35 m

svdp.xaxis.tick_top() # move the x-axis to the top of the plot
svdp.xaxis.set_label_position('top') # move the x-axis label to the top of the plot

# Add the legend
plt.legend()

# Titles and stuff
plt.title('Shear velocity depth profile')
plt.xlabel('Shear wave velocity (m/s)')
plt.ylabel('Depth (m)')

# Save the plot as a file
plt.savefig(output_file_name)

# Display the plot
plt.show()