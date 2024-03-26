from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.Tables import Tables

from RPA.PDF import PDF

from RPA.Archive import Archive 

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_the_robot_website()
    close_annoying_modal()
    download_csv_file()
    orders = get_orders()
    fill_the_form(orders)

    archive_receipts()

def open_the_robot_website():
    """Open a URL website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
def get_orders():
    """Create a table from csv file"""
    csv = Tables()
    orders = csv.read_table_from_csv(
        "orders.csv", columns=["Order number","Head","Body","Legs","Address"]
    )

    return orders 

def fill_the_form(orders):
    """Create the diferent robots"""
    page = browser.page()
    
    for order in orders:
        page.locator("//select[@name='head']").select_option(index=int(order["Head"]))       
        page.locator("//input[@id=" + "'" + "id-body-" + order["Body"] + "']").click()
        page.locator("//input[@placeholder='Enter the part number for the legs']").fill(order["Legs"])
        page.locator("//input[@name='address']").fill(order["Address"])

        page.locator("//button[@id='preview']").click()
        page.locator("//button[@id='order']").click()
               
        #Check error
        orden_another = page.query_selector("//button[@id='order-another']")
        
        #error
        if orden_another:
            #
            path_pdf = store_receipt_as_pdf(order["Order number"])
            path_screenshot = screenshot_robot(order["Order number"])
            embed_screenshot_to_receipt(path_screenshot, path_pdf)
            #
            page.locator("//button[@id='order-another']").click()
            close_annoying_modal()
        else:
            error_save_robot = True
            while error_save_robot == True:
                page.locator("//button[@id='order']").click()
                orden_another = page.query_selector("//button[@id='order-another']")
                if orden_another:
                    error_save_robot = False
                    #
                    path_pdf = store_receipt_as_pdf(order["Order number"])
                    path_screenshot = screenshot_robot(order["Order number"])
                    embed_screenshot_to_receipt(path_screenshot, path_pdf)
                    #
                    page.locator("//button[@id='order-another']").click()
                    close_annoying_modal()

def store_receipt_as_pdf(order_number):
    """PDF with the diferent robots created"""
    page = browser.page()
    order_robot_html = page.locator("#receipt").inner_html()
    
    pdf = PDF()
    path_pdf = "./output/receipt/" + str(order_number) + ".pdf"
    pdf.html_to_pdf(order_robot_html, path_pdf)

    return path_pdf 

def screenshot_robot(order_number):
    """Screenshot with the diferent robots"""
    page = browser.page()
    path_screenshot = "./output/receipt/" + str(order_number) + ".png"
    page.screenshot(path=path_screenshot)

    return path_screenshot 

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the robot screenshot to the receipt PDF file"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, 
                                   source_path=pdf_file, 
                                   output_path=pdf_file)
    
def archive_receipts():
    """Create a zip file"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipt/","./output/receipt/receipt.zip")
