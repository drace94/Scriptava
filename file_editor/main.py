from file_editor import activity

file_path = ['file1.tcx', 'file2.tcx', 'file3.tcx']

for file in file_path:

    act = activity(file)
    act.summarize()
