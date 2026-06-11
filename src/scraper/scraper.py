import time
import uuid
from pathlib import Path

from playwright.async_api import async_playwright

from src.models.search_model import SearchRequest


async def run_serff_search(search_request: SearchRequest) -> dict:
    """
    Handles the Playwright lifecycle independently.
    Accepts raw python arguments and returns a dictionary of results.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            await page.goto(
                f"https://filingaccess.serff.com/sfa/home/{search_request.state}"
            )
            button = page.locator("#bodyContentWrapper > div > a")

            # Explicitly wait for it to be visible on the screen
            await button.wait_for(state="visible", timeout=5000)
            await button.click()

            await page.get_by_role("button", name="Accept").click()

            await page.locator('[id="simpleSearch:businessType_label"]').click()
            await page.locator(
                f'li[data-label="{search_request.business_type}"]'
            ).click()

            await page.locator(
                "label.ui-selectcheckboxmenu-label:has-text('Type of Insurance')"
            ).click()

            for insurance_type in search_request.type_of_insurance:
                option_checkbox = page.locator(
                    f'div.ui-selectcheckboxmenu-items-wrapper label:has-text("{insurance_type}")'
                )
                # Wait for the option to be visible and click it
                await option_checkbox.wait_for(state="visible", timeout=2000)
                await option_checkbox.click()

            await page.locator(
                "a.ui-selectcheckboxmenu-close:has-text('Close')"
            ).click()

            await page.locator('[id="simpleSearch:productName"]').fill(
                search_request.insurance_product_name
            )

            # TODO: Add in a search request for contains vs the other one
            await page.locator('label[for="simpleSearch:productNameOptions:1"]').click()

            await page.locator('[id="simpleSearch:saveBtn"]').click()

            # 1. Wait for the table structure to fully render on the page
            await page.wait_for_selector(".ui-datatable-tablewrapper table")

            # 2. Extract column headers dynamically
            header_elements = await page.query_selector_all(
                ".ui-datatable-tablewrapper thead th"
            )
            headers = []
            for th in header_elements:
                title_element = await th.query_selector(".ui-column-title")
                if title_element:
                    title_text = await title_element.inner_text()
                    headers.append(title_text.strip())
                else:
                    headers.append("")

            # 3. Extract all data rows from the table body
            row_elements = await page.query_selector_all(
                ".ui-datatable-tablewrapper tbody tr"
            )
            parsed_table_data = []

            for row_idx, row in enumerate(row_elements):
                # Get all cell elements for the current row
                cells = await row.query_selector_all("td")

                # Skip empty or loading rows if any exist
                if not cells or len(cells) != len(headers):
                    continue

                row_data = {}
                for index, cell in enumerate(cells):
                    cell_text = await cell.inner_text()
                    column_name = headers[index]

                    # Clean up column text and map it
                    if column_name:
                        row_data[column_name] = cell_text.strip()

                if row_data.get("Filing Type") == "Form":
                    row_data["row_index"] = row_idx
                    parsed_table_data.append(row_data)

            print(parsed_table_data)
            await page.locator('tr[data-ri="1"]').click()

            unique_id = str(uuid.uuid4())
            target_path = Path(".") / unique_id
            target_path.mkdir(parents=True, exist_ok=True)
            print(f"Folder created successfully at: {target_path.resolve()}")

            for data in parsed_table_data:
                row_index = data["row_index"]
                company_name = data["Company Name"]
                serff_tracking_number = (
                    data["SERFF Tracking Number"]
                    .replace(" ", "_")
                    .replace("&", "and")
                    .replace(",", "")
                    .replace(".", "")
                    .lower()
                )
                target_path = Path(".") / unique_id / company_name
                target_path.mkdir(parents=True, exist_ok=True)
                await page.locator(f'tr[data-ri="{row_index}"]').click()

                form_button = page.locator("#formAttachmentSelectCurrentButton")
                await form_button.wait_for(state="attached", timeout=5000)
                await form_button.click()
                await page.wait_for_timeout(300)

                async with page.expect_download() as download_info:
                    await page.locator('[id="summaryForm:downloadLink"]').click()
                download = await download_info.value

                # 2. Save the ZIP file locally to your machine
                zip_path = target_path / f"{serff_tracking_number}.zip"
                await download.save_as(zip_path)

                print(f"Zip file successfully downloaded and saved to {zip_path}")
                await page.get_by_role(
                    "button", name="Return to Search Results"
                ).click()
            time.sleep(3)
            # if company_name:
            #     await page.fill("input#company-name-input", company_name)
            # if business_type:
            #     await page.fill("input#business-type-input", business_type)
            # await page.click("button#search-submit-btn")
            # await page.wait_for_selector(".search-results-list", timeout=10000)

            # # Extract data
            # result_elements = await page.query_selector_all(".result-item-title")
            # scraped_results = []

            # for element in result_elements:
            #     text = await element.inner_text()
            #     scraped_results.append({"title": text.strip()})

            # await browser.close()
            return {"status": "success"}

        except Exception as e:
            await browser.close()
            raise e
