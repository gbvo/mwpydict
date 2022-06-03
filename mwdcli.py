#! /home/cooper/Codes/venv/bin/python
import colors
from mwd import MWD
import subprocess
import readline


def colorize(color, text):
    return color + text + colors.NORMAL


class DictPrinter:

    def __init__(self, query):
        self.query = query
        self.data = MWD(query).parse()
        self.text = ''

    def pretty_print(self):
        for entry in self.data:
            self.print_entry(entry)
            self.text += '\n\n'
        return self.text

    def print_entry(self, entry):
        for key, value in entry.items():
            if key == 'headword':
                self.print_headword(value)
            elif key == 'hw_infos':
                self.print_hw_infos(value)
            elif key == 'snote':
                self.print_snote(value)
            elif key == 'entry_labels':
                self.print_entry_labels(value)
                self.text += '\n'
            elif key == 'sblocks':
                self.print_sblocks(value)
                self.text += '\n'
            elif key == 'dros':
                self.print_dros(value)
                self.text += '\n'
            elif key == 'uros':
                self.text += '\n'
                self.print_uros(value)

    def print_headword(self, headword):
        headword_text = headword.get('headword_text', '')
        headword_prons = headword.get('headword_prons', '')
        fl = headword.get('fl', '')
        homograph = headword_text.get('homograph', '')
        text = headword_text.get('text', '')

        if homograph:
            self.text += colorize(colors.BOLDRED, homograph) + ' '

        self.text += colorize(colors.BOLDGREEN, text) + ' '
        for pron in headword_prons:
            self.text += pron + ' '

        self.text += fl + '\n'

    def print_hw_infos(self, hw_infos):
        for key, value in hw_infos:
            if key == 'i_label':
                self.text += colorize(colors.MAGENTA, value) + ' '
            else:
                self.text += value + ' '
        self.text += '\n'

    def print_snote(self, snote):
        both_text = snote.get('both_text', '')
        snote_text = snote.get('snote_text', '')
        self.text += ' '.join([snote_text, both_text])
        # self.text += '\n'

    def print_entry_labels(self, entry_labels):
        for key, value in entry_labels:
            self.text += value + ' '

    def print_sblocks(self, sblocks):
        for sblock in sblocks:
            sn_block_num = sblock.get('sn_block_num', '')
            scnt = sblock.get('scnt', '')
            self.text += colorize(colors.BOLDCYAN, sn_block_num) + ' '

            for key, value in scnt.items():
                if key == 'sblock_labels':
                    for labelk, labelv in value:
                        self.text += labelv + ' '
                elif key == 'senses':
                    for sense in value:
                        for sensek, sensev in sense:
                            if sensek == 'def_text':
                                self.text \
                                    += colorize(colors.YELLOW, sensev) + ' '
                            elif sensek == 'vis_w':
                                self.print_vis_w(sensev)
                            elif sensek == 'sn_letter':
                                self.text += colorize(
                                    colors.BOLDMAGENTA, sensev) + ' '
                            elif sensek == 'snote':
                                self.print_snote(sensev)
                            elif sensek == 'usage_par':
                                self.print_usage_par(sensev)
                            elif sensek == 'un_text':
                                self.text \
                                    += colorize(colors.MAGENTA, sensev) + ' '
                            else:
                                self.text += sensev + ' '
            self.text += '\n'
        self.text = self.text[:-1]

    def print_vis_w(self, vis_w):
        for vi in vis_w:
            mw_spms = \
                vi.get('mw_spm_its', []) + vi.get('mw_spm_phrases', [])
            vi_text = vi.get('vi_text')
            vi_text = colorize(colors.WHITE, vi_text)
            for mw in mw_spms:
                vi_text = \
                    vi_text.replace(
                        mw, '\x1B[1m{}\x1B[0m\033[0;37m'.format(mw))
            self.text += '//' + vi_text + ' '

    def print_usage_par(self, usage_par):
        for k, v in usage_par.items():
            if k == 'usage_par_h':
                self.text += v + ' '
            elif k == 'ud_text':
                self.text += v + ' '
            elif k == 'vis_w':
                self.print_vis_w(v)

    def print_dros(self, dros):
        for dro in dros:
            for k, v in dro:
                if k == 'dro_line':
                    for class_, value in v:
                        if class_ == 'dre':
                            self.text \
                                += colorize(colors.BOLDBLUE, value) + ' '
                        else:
                            self.text += value + ' '
                elif k == 'sblocks':
                    self.text += '\n'
                    self.print_sblocks(v)
                elif k == 'dxs':
                    self.text += v + ' '
            self.text += '\n'
        self.text = self.text[:-1]

    def print_uros(self, uros):
        for uro in uros:
            for k, v in uro.items():
                if k == 'uro_line':
                    for class_, value in v:
                        if class_ == 'ure':
                            self.text += colorize(
                                colors.GREEN, value
                            ) + ' '
                        else:
                            self.text += value + ' '
                elif k == 'uro_def':
                    for class_, value in v:
                        if class_ == 'vis_w':
                            self.print_vis_w(value)
            self.text += '\n'
        self.text = self.text[:-1]


def main():
    print(readline)
    while True:
        query = input('word: ')
        printer = DictPrinter(query)
        subprocess.run('clear')
        subprocess.run((['less', '-R']), input=printer.pretty_print(),
                       encoding='utf-8')
    # query = 'quite'
    # printer = DictPrinter(query)
    # print(printer.pretty_print())


if __name__ == '__main__':
    main()
