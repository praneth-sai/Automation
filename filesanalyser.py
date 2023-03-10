import os
import zipfile
import pandas as pd

# Function to get file size in bytes
def get_file_size(file_path):
    return os.path.getsize(file_path)

# Function to extract file extension
def get_file_extension(file_path):
    return os.path.splitext(file_path)[1]

# Function to create an Excel file with file names, extensions, and sizes
def create_excel_file(zip_path, excel_file_path):
    # Read the file names and sizes from the zip file
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        file_info_list = [(name, get_file_extension(name), get_file_size(zip_file.extract(name))) for name in zip_file.namelist()]

    # Create a pandas DataFrame from the file info
    file_info_df = pd.DataFrame(file_info_list, columns=["File Name", "Extension", "Size"])

    # Group the file info by extension and sum the sizes
    file_info_grouped_df = file_info_df.groupby("Extension").agg({"File Name": "count", "Size": "sum"}).reset_index()

    # Sort the file info by size
    file_info_sorted_df = file_info_grouped_df.sort_values("Size", ascending=False)

    # Write the file info to an Excel file
    with pd.ExcelWriter(excel_file_path) as writer:
        file_info_sorted_df.to_excel(writer, sheet_name="File Info", index=False)

        # Add a pivot table to the Excel file
        pivot_table_df = file_info_sorted_df.pivot_table(index="Extension", values=["File Name", "Size"], aggfunc={"File Name": "sum", "Size": "sum"})
        pivot_table_df.to_excel(writer, sheet_name="Pivot Table")

        # Add a chart to the Excel file
        chart_sheet = writer.book.add_worksheet("Chart")
        chart = writer.book.add_chart({"type": "column"})
        chart.add_series({"name": "Size", "categories": "=Pivot Table!$A$2:$A${}".format(len(pivot_table_df)+1), "values": "=Pivot Table!$C$2:$C${}".format(len(pivot_table_df)+1)})
        chart.set_title({"name": "File Sizes by Extension"})
        chart.set_x_axis({"name": "Extension"})
        chart.set_y_axis({"name": "Size (bytes)"})
        chart_sheet.insert_chart("A1", chart)


# Example usage
zip_path = input("Enter the path to the zipped source code: ")
excel_file_path = input("Enter the path to the output Excel file: ")
create_excel_file(zip_path, excel_file_path)
