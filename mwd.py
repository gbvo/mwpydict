import bs4
from bs4 import BeautifulSoup
import requests
import json
import re


def get_soup(query):
    url = 'https://learnersdictionary.com/definition/%s' % query
    headers = {
        'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64; rv:89.0)'
                       ' Gecko/20100101 Firefox/89.0')
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')\
        if page.status_code == 200 else None
    return soup


class MWD:

    def __init__(self, query):
        self.query = query
        self.soup = get_soup(query)

    def parse(self):
        entries_json = []
        if self.soup:
            entries = self.soup.find_all('div', class_='entry')
            for entry in entries:
                entries_json.append(self.parse_entry(entry))

        return entries_json

    def parse_entry(self, entry):
        entry_json = {}

        for child in entry.children:
            if isinstance(child, bs4.element.Tag):
                class_ = child.attrs['class'][0]
                if class_ == 'hw_d':
                    entry_json['headword'] = self.parse_headword(child)
                elif class_ == 'hw_infs_d':
                    entry_json['hw_infos'] = self.parse_hw_infos(child)
                elif class_ == 'snote':
                    entry_json['snote'] = self.parse_snote(child)
                elif class_ == 'labels':
                    entry_json['entry_labels'] = self.parse_entry_labels(child)
                elif class_ == 'sblocks':
                    entry_json['sblocks'] = self.parse_sblocks(child)
                elif class_ == 'dxs':
                    entry_json['dxs'] \
                        = re.sub(r'\s+', ' ', child.get_text()).strip()
                elif class_ == 'dros':
                    entry_json['dros'] = self.parse_dros(child)
                elif class_ == 'uros':
                    entry_json['uros'] = self.parse_uros(child)

        return entry_json

    def parse_headword(self, headword):
        headword_json = {}
        headword_text = headword.find('span', class_='hw_txt')
        headword_prons = headword.find_all('span', class_='hpron_word')
        fl = headword.find('span', class_='fl')
        if headword_text:
            headword_text_json = {}
            for child in headword_text.children:
                if isinstance(child, bs4.element.Tag):
                    if child.attrs['class'][0] == 'homograph':
                        headword_text_json['homograph'] = child.get_text()
                elif isinstance(child, bs4.element.NavigableString):
                    headword_text_json['text'] = child.strip()

            headword_json['headword_text'] = headword_text_json

        if headword_prons:
            headword_prons_json = []
            for hpron in headword_prons:
                hpron_json = hpron.get_text().strip()
                headword_prons_json.append(hpron_json)

            headword_json['headword_prons'] = headword_prons_json

        if fl:
            headword_json['fl'] = fl.get_text().strip()

        return headword_json

    def parse_hw_infos(self, hw_infos):
        hw_infos_json = []
        if hw_infos:
            for child in hw_infos.children:
                if isinstance(child, bs4.element.Tag):
                    class_ = child.attrs['class'][0]
                    if class_ in ['i_label', 'i_text', 'pron_w', 'semicolon']:
                        value = child.get_text().strip()
                        hw_infos_json.append((class_, value))
        return hw_infos_json

    def parse_snote(self, snote):
        snote_json = {}
        for child in snote.children:
            if isinstance(child, bs4.element.Tag):
                class_ = child.attrs['class'][0]
                if class_ == 'vis_w':
                    snote_json['vis_w'] = self.parse_vis_w(child)
                elif class_ == 'snote_text':
                    snote_json['snote_text'] = child.get_text().strip()
                elif class_ == 'both_text':
                    snote_json['both_text'] = child.get_text().strip()

        return snote_json

    def parse_entry_labels(self, entry_labels):
        entry_labels_json = []
        if entry_labels:
            for child in entry_labels.children:
                if isinstance(child, bs4.element.Tag):
                    class_ = child.attrs['class'][0]
                    value = child.get_text().strip()
                    entry_labels_json.append((class_, value))
        return entry_labels_json

    def parse_sblocks(self, sblocks):
        sblocks_json = []
        sblocks = sblocks.find_all('div', class_='sblock_c')
        for sblock_c in sblocks:
            sblock_c_json = {}
            sn_block_num = sblock_c.find('strong', class_='sn_block_num')
            scnt = sblock_c.find('div', class_='scnt')
            if sn_block_num:
                sblock_c_json['sn_block_num'] = sn_block_num.get_text().strip()
            sblock_c_json['scnt'] = self.parse_scnt(scnt)

            sblocks_json.append(sblock_c_json)

        return sblocks_json

    def parse_scnt(self, scnt):
        scnt_json = {}
        if scnt:
            sblock_labels = scnt.find('div', class_='sblock_labels')
            senses = scnt.find_all('div', class_='sense')
            if sblock_labels:
                scnt_json['sblock_labels'] \
                    = self.parse_sblock_labels(sblock_labels)
            if senses:
                senses_json = []
                for sense in senses:
                    senses_json.append(self.parse_sense(sense))
                scnt_json['senses'] = senses_json

        return scnt_json

    def parse_sblock_labels(self, sblock_labels):
        sblock_labels_json = []
        for child in sblock_labels.children:
            if isinstance(child, bs4.element.Tag):
                class_ = child.attrs['class'][0]
                value = child.get_text().strip()
                # print(value, len(value))
                sblock_labels_json.append((class_, value))

        return sblock_labels_json

    def parse_sense(self, sense):
        sense_json = []
        for child in sense.children:
            if isinstance(child, bs4.element.Tag):
                class_ = child.attrs['class'][0]
                if class_ == 'vis_w':
                    value = self.parse_vis_w(child)
                elif class_ == 'dxs':
                    value = re.sub(r'[\s]+', ' ', child.get_text()).strip()
                elif class_ == 'isyns':
                    value = re.sub(r'\s+', ' ', child.get_text().strip())
                elif class_ == 'snote':
                    value = self.parse_snote(child)
                elif class_ == 'usage_par':
                    value = self.parse_usage_par(child)
                elif class_ == 'cas':
                    value = re.sub(r'\s+', ' ', child.get_text().strip())
                elif class_ == 'synref_block':
                    value = re.sub(r'\s+', ' ', child.get_text().strip())
                else:
                    value = child.get_text().strip()
                sense_json.append((class_, value))

        return sense_json

    def parse_vis_w(self, vis_w):
        vis_w_json = []
        vis = vis_w.find_all('li', class_='vi')
        for vi in vis:
            vi_json = {}
            vi_content = vi.find('div', class_='vi_content')
            vi_text = vi_content.get_text().strip()
            vi_json['vi_text'] = vi_text
            mw_spm_its = vi_content.find_all('em', class_='mw_spm_it')
            vi_json['mw_spm_its'] \
                = [msi.get_text().strip() for msi in mw_spm_its]
            mw_spm_phrases \
                = vi_content.find_all('span', class_='mw_spm_phrase')
            vi_json['mw_spm_phrases'] \
                = [msp.get_text().strip() for msp in mw_spm_phrases]

            vis_w_json.append(vi_json)
        return vis_w_json

    def parse_dros(self, dros):
        dros_json = []
        dros = dros.find_all('div', class_='dro')
        for dro in dros:
            dro_json = []
            for child in dro.children:
                if isinstance(child, bs4.element.Tag):
                    class_ = child.attrs['class'][0]
                    if class_ == 'dro_line':
                        value = self.parse_dro_line(child)
                    elif class_ == 'dxs':
                        value = re.sub(r'[\s]+', ' ', child.get_text()).strip()
                    elif class_ == 'sblocks':
                        value = self.parse_sblocks(child)
                    dro_json.append((class_, value))
            dros_json.append(dro_json)

        return dros_json

    def parse_dro_line(self, dro_line):
        dro_line_json = []
        for child in dro_line.children:
            if isinstance(child, bs4.element.Tag):
                class_ = child.attrs['class'][0]
                value = child.get_text().strip()
                dro_line_json.append((class_, value))
        return dro_line_json

    def parse_usage_par(self, usage_par):
        usage_par_json = {}
        usage_par_h = usage_par.find('span', class_='usage_par_h')
        ud_text = usage_par.find('span', class_='ud_text')
        vis_w = usage_par.find('div', class_='vis_w')
        if usage_par_h:
            usage_par_json['usage_par_h'] = usage_par_h.get_text().strip()
        if ud_text:
            usage_par_json['ud_text'] = ud_text.get_text().strip()
        if vis_w:
            usage_par_json['vis_w'] = self.parse_vis_w(vis_w)

        return usage_par_json

    def parse_uros(self, uros):
        uros_json = []
        if uros:
            uros = uros.find_all('div', class_='uro')
            for uro in uros:
                uro_json = {}
                for child in uro.children:
                    if isinstance(child, bs4.element.Tag):
                        class_ = child.attrs['class'][0]
                        if class_ == 'uro_line':
                            uro_json['uro_line'] = self.parse_uro_line(child)
                        elif class_ == 'uro_def':
                            uro_json['uro_def'] = self.parse_uro_def(child)
                uros_json.append(uro_json)
        return uros_json

    def parse_uro_line(self, uro_line):
        uro_line_json = []
        for child in uro_line.children:
            if isinstance(child, bs4.element.Tag):
                class_ = child.attrs['class'][0]
                value = child.get_text().strip()
                uro_line_json.append((class_, value))
        return uro_line_json

    def parse_uro_def(self, uro_def):
        uro_def = uro_def.find('div', class_='uro_def')
        uro_def_json = []
        if uro_def:
            for child in uro_def.children:
                if isinstance(child, bs4.element.Tag):
                    class_ = child.attrs['class'][0]
                    if class_ == 'vis_w':
                        value = self.parse_vis_w(child)
                    else:
                        value = child.get_text().strip()
                    uro_def_json.append((class_, value))
        return uro_def_json


def main():
    mwd = MWD('corresponding')
    # mwd.parse()
    json.dump(mwd.parse(), open('test.json', 'w'), indent=4)


if __name__ == '__main__':
    main()
