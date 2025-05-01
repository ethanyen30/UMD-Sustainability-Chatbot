import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

class UMDWebScraper:
    def __init__(self, url):
        self.url = url
        self.visited_links = set()
        self.data = []
        self.template_data = {
            "Link": "",
            "Site_Title": "",
            "Header": "",
            "Content": "",
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def extract_links(self, soup, base_url):
        links = set()
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(base_url, a_tag["href"])
            if link.startswith(self.url) and link not in self.visited_links \
            and not link.startswith(self.url + "sites/default/files") \
            and '#' not in link and '?' not in link:
                links.add(link)
        return links

    def extract_content(self, soup, page_template):
        main_content = self.get_main_content(soup, page_template)
        text_content = self.get_text_content(soup, page_template)
        accordion_content = self.get_accordion_content(soup, page_template)
        card_group_content = self.get_card_groups(soup, page_template)
        slideshow_content = self.get_slideshow_data(soup, page_template)

        content = main_content + text_content + accordion_content + card_group_content + slideshow_content
        return self.clean_contents(content)

    def scrape(self, url):
        if url in self.visited_links:
            return

        print(f"Scraping: {url}")
        self.visited_links.add(url)

        soup = self.fetch_page(url)
        if not soup:
            return

        page_template = self.template_data.copy()
        page_template['Link'] = url
        page_template['Site_Title'] = soup.title.string

        self.data += self.extract_content(soup, page_template)

        new_links = self.extract_links(soup, url)
        for link in new_links:
            self.scrape(link)

    def save_data(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {filename}")

    def get_main_content(self, soup, page_template):
        main_data = []

        mc = soup.find(id='main-content')
        if mc:
            ec = mc.find(class_='editor-content')
            if ec:
                new_data = page_template.copy()
                for child in ec.children:
                    if child.name in ['h1', 'h2', 'h3']:
                        main_data.append(new_data)
                        new_data = page_template.copy()
                        new_data['Header'] = child.get_text()

                    if child.name == 'p':
                        new_data['Content'] += child.get_text(strip=True) + " "

                    if child.name == 'ul':
                        for li in child.find_all('li'):
                            new_data['Content'] += li.get_text() + " "
                if new_data:
                    main_data.append(new_data)

        return main_data

    def get_text_content(self, soup, page_template):
        text_data = []
        editor_content = []

        psuft = soup.find_all(class_='page-section-ut_feature')
        sutf = soup.find_all(class_='section-ut_feature')
        psutt = soup.find_all(class_='page-section-ut_text')
        sutt = soup.find_all(class_='section-ut_text')
        psutiwt = soup.find_all(class_='page-section-ut_image_with_text')
        sutiwt = soup.find_all(class_='section-ut_image_with_text')

        search = psuft + sutf + psutt + sutt + psutiwt + sutiwt
        for thing in search:
            for ec in thing.find_all(class_='editor-content'):
                editor_content.append(ec)

        for ec in editor_content:
            new_data = page_template.copy()

            ul = ec.find('ul')
            if ul:
                for li in ul.find_all('li'):
                    list_data = new_data.copy()
                    list_data['Content'] = li.get_text()
                    text_data.append(list_data)

            header1 = ec.find('h1')
            if header1:
                new_data['Header'] = header1.get_text()
            else:
                header2 = ec.find('h2')
                if header2:
                    new_data['Header'] = header2.get_text()
                else:
                    header3 = ec.find('h3')
                    if header3:
                        new_data['Header'] = header3.get_text()
                    else:
                        header4 = ec.find('h4')
                        if header4:
                            new_data['Header'] = header4.get_text()

            ps = ec.find_all('p')
            if ps:
                for p in ps:
                    new_data['Content'] += p.get_text() + " "
            else:
                spans = ec.find_all('span')
                if spans:
                    for span in spans:
                        new_data['Content'] = span.get_text() + " "

            text_data.append(new_data)

        return text_data

    def get_accordion_content(self, soup, page_template):
        accordion_data = []

        for a in soup.find_all(class_='accordion'):
            for card in a.find_all(class_='card'):
                new_data = page_template.copy()

                ch = card.find(class_='card-header')
                if ch:
                    new_data['Header'] = ch.get_text(strip=True)

                cb = card.find(class_='card-body')
                if cb:
                    new_data['Content'] = cb.get_text(strip=True)

                accordion_data.append(new_data)

        return accordion_data

    def get_card_groups(self, soup, page_template):
        card_groups = []

        for cg in soup.find_all(class_='card-group'):
            for cw in cg.find_all(class_='card-wrap'):
                new_data = page_template.copy()

                ctitle = cw.find(class_='card-title')
                if ctitle:
                    new_data['Header'] = ctitle.get_text(strip=True)

                ctext = cw.find(class_='card-text')
                if ctext:
                    new_data['Content'] = ctext.get_text(strip=True)

                card_groups.append(new_data)

        return card_groups

    def get_slideshow_data(self, soup, page_template):
        slideshow_data = []

        sus = soup.find_all(class_='section-ut_slideshow')
        psuts = soup.find_all(class_='page-section-ut_slideshow')

        search = sus + psuts
        for thing in search:
            for si in thing.find_all(class_='slideshow-item'):
                new_data = page_template.copy()

                sct = si.find(class_='slideshow-caption-title')
                if sct:
                    new_data['Header'] = sct.get_text()

                scc = si.find(class_='slideshow-caption-content')
                if scc:
                    new_data['Content'] = scc.get_text()

                slideshow_data.append(new_data)

        return slideshow_data

    def clean_contents(self, data):
        cleaned_data = []
        for chunk in data:
            if len(chunk['Content']) < 50:
                continue
            chunk['Content'] = chunk['Content'].replace("\xa0", " ")
            cleaned_data.append(chunk)

        return cleaned_data