"""
Uses pandas to convert a dataframe into an Excel sheet.

Add the data
then create_excel()
"""


import pandas as pd
import os


class ExcelCreator:
    def __init__(self, folder, file_name, sheet_name='Sheet1'):
        """
        Initializes the ExcelCreator with a file name and optional sheet name.

        :param file_name: The name of the Excel file to create (without extension).
        :param sheet_name: The name of the sheet in the Excel file.
        """
        self.data_frame = pd.DataFrame()
        self.sheet_name = sheet_name
        self.dir = folder

        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
            print(f"Directory '{self.dir}' created.")

        self.file_name = self.dir + "/" + file_name

    def set_entire_data(self, data, columns=None):
        """
        Sets the data for the Excel file.

        :param data: Data to populate the DataFrame. Can be a dict, list of dicts, etc.
        :param columns: Optional list of column names.
        """
        self.data_frame = pd.DataFrame(data, columns=columns)

    def add_column(self, column_name, data):
        """
        Adds a column to the DataFrame.

        :param column_name: The name of the column to add.
        :param data: The data for the column. Must match the length of the current DataFrame.
        """
        if len(data) != len(self.data_frame) and not self.data_frame.empty:
            raise ValueError(
                f"Length of data ({len(data)}) does not match the number of rows in the DataFrame ({len(self.data_frame)}).")

        self.data_frame[column_name] = data

    def add_row(self, data):
        """
        Adds a row to the DataFrame.

        :param data: The row data to add. Length must match the number of columns.
        """
        if len(data) != len(self.data_frame.columns):
            raise ValueError(
                f"Row length ({len(data)}) does not match the number of columns in the DataFrame ({len(self.data_frame.columns)}).")

        # Append the new row to the DataFrame
        self.data_frame.loc[len(self.data_frame)] = data

    def reorder_columns(self, new_order):
        """
        Reorders the columns of the DataFrame.

        :param new_order: A list of column names in the desired order.
        """
        if set(new_order) != set(self.data_frame.columns):
            print(f"given: \n{new_order} \ndoes not match with current set: \n{self.data_frame.columns}")
            for item in new_order:
                if item not in self.data_frame.columns:
                    print(f"ERROR: {item}  NOT IN NEW SET")
            raise ValueError("New column order does not match the current columns.")

        # Reorder the columns
        self.data_frame = self.data_frame[new_order]

    def excel_column_name(self, n):
        """Convert a column index (0-based) to an Excel-style column name."""
        name = ""
        while n >= 0:
            name = chr(n % 26 + 65) + name
            n = n // 26 - 1
        return name

    def create_excel(self, apply_style=True):
        """
        Creates an Excel file with the current DataFrame data, with optional table styling.

        :param apply_style: If True, formats the data as an Excel table. Defaults to True.
        """
        if self.data_frame.empty:
            raise ValueError("The DataFrame is empty. Please set the data before creating the Excel file.")

        # Use a context manager to ensure the writer is properly closed
        with pd.ExcelWriter(f"{self.file_name}.xlsx", engine="xlsxwriter") as writer:
            # Write the DataFrame to the Excel file
            self.data_frame.to_excel(writer, sheet_name=self.sheet_name, index=False)

            # Access the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets[self.sheet_name]

            if apply_style:
                # Get the dimensions of the DataFrame
                (max_row, max_col) = self.data_frame.shape

                # Define the range for the table
                table_range = f"A1:{self.excel_column_name(max_col - 1)}{max_row + 1}"
                # table_range = f"A1:{chr(64 + max_col)}{max_row + 1}"  # Assuming max_col <= 26

                # Create a list of column headers for the table
                column_settings = [{"header": column} for column in self.data_frame.columns]

                # Add the Excel table structure. Pandas has already written the data.
                worksheet.add_table(table_range, {"columns": column_settings, "autofilter": True})

                # Set the column widths for better readability
                worksheet.set_column(0, max_col - 1, 15)

        print(f"Excel file '{self.file_name}.xlsx' created successfully.")
