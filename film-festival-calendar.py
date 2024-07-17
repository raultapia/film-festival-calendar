import datetime
import re
import requests


def shift_month(date1, date2):
    if int(date1[6:8]) > int(date2[6:8]):
        x = str(int(date1[4:6]) - 1)
        return (date1[:4] + (x if len(x) > 1 else f"0{x}") + date1[6:], date2)
    return (date1, date2)


def date_to_ics_format(date):
    date = date.replace(".", " ")
    d = date.lstrip().rstrip().replace(", ", " ").replace(" - ", " ").replace("-", " ").replace("–", " ").replace("/", " ").replace("for the", "").split()
    if not d[0].isnumeric() and not d[2].isnumeric():
        del d[0]
        d[1], d[2] = d[2], d[1]
    if not d[0].isnumeric():
        d.insert(2, d.pop(0))
    if len(d) > 4:
        del d[1]
    if not d[2].isnumeric():
        d[2] = str(datetime.datetime.strptime(d[2], '%B').month)
    d = [x if len(x) > 1 else f"0{x}" for x in d]
    return shift_month(f'{d[3]}{d[2]}{d[0]}', f'{d[3]}{d[2]}{d[1]}')


class Calendar:
    def __enter__(self):
        self.text = "BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\nMETHOD:PUBLISH\nX-WR-CALNAME:Film Festivals\n"
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        with open("film-festival-calendar.ics", "w") as f:
            f.write(self.text + "END:VCALENDAR")

    def add(self, event):
        self.text += str(event)


class Festival:
    def __init__(self, name, url, dateparser):
        self.name = name
        self.url = url
        self.dateparser = dateparser

    def __str__(self):
        print(self.dateparser(requests.get(self.url).text).group(1))
        date = date_to_ics_format(self.dateparser(requests.get(self.url).text).group(1))
        return f"BEGIN:VEVENT\nDTSTART:{date[0]}\nDTEND:{date[1]}\nSUMMARY:{self.name}\nDESCRIPTION:Imported from https://github.com/raultapia/film-festival-calendar\nEND:VEVENT\n"


if __name__ == "__main__":
    with Calendar() as cal:
        cal.add(Festival("Sitges Film Festival", "https://sitgesfilmfestival.com/en", lambda text: re.search(r'<p>(.*?)</p>', text)))
        cal.add(Festival("Cannes Film Festival", "https://www.festival-cannes.com/en/", lambda text: re.search(r'<em>(.*?)</em>', text)))
        cal.add(Festival("Festival de Cine Europeo de Sevilla (SEFF)", "https://festivalcinesevilla.eu/en", lambda text: re.search(r'item">(.*?)</div>', text)))
        cal.add(Festival("Toronto International Film Festival (TIFF)", "https://www.tiff.net/about-the-festival", lambda text: re.search(r'<div class="label-container">(.*?)</div>', text, re.DOTALL)))
        cal.add(Festival("Festival Internacional de Cine de San Sebastian (SSIFF)", "https://www.sansebastianfestival.com/home/2/in", lambda text: re.search(r'</strong> -(.*?)</span>', text)))
        cal.add(Festival("Berlin International Film Festival (Berlinale)", "https://www.berlinale.de/en/dates.html", lambda text: re.search(r'middle;">(.*?)</th>', text)))
        cal.add(Festival("Mostra Internazionale d'Arte Cinematografica della Biennale di Venezia", "https://www.labiennale.org/it/cinema", lambda text: re.search(r'Lido di Venezia, (.*?)</div>', text)))
        cal.add(Festival("Sundance Film Festival", "https://festival.sundance.org/", lambda text: re.search(r'Join us(.*?)Sundance', text)))
        # cal.add(Festival("Semana Internacional de Cine de Valladolid (SEMINCI)", "https://www.seminci.com/en/home/", lambda text: re.search(r'edition.</strong> (.*?)</div>', text)))
