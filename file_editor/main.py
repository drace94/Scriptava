from file_editor import activity

file_dir = './test_files/'
file_name = ['file1.tcx', 'file2.tcx', 'file3.tcx', 'file1.gpx']

for file in file_name:

    act = activity(file_dir+file)
    act.summarize()
