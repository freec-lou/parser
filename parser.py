# -*- coding:utf-8 -*-
"""
Выполняется распознавание строки команды с командой 07.

Запуск скрипта:

    python parser.py [исходный_файл] [отформатированный_файл]

    ВАЖНО! Не перепутать параметры местами, иначе исходный файл будет перезаписан.
Формат данных распознанной строки:

    [Tag] : [Длина данных] [Данные]

"""
import time
import re
import sys

# Номера тегов в hex формате.
tags = ('E903', 'EA03', 'EB03', 'EC03', 'ED03', 'EE03', 'EF03', 'F003', 'F103',
        'F203', 'F303', 'F403', 'F503', 'F603', 'F703', 'F803', 'F903', 'FA03',
        'FB03', 'FC03', 'FD03', 'FE03', 'FF03', '0004', '0104', '0204', '0304',
        '0404', '0504', '0604', '0704', '0A04', '0B04', '0C04', '0D04', '0E04',
        '0F04', '1004', '1104', '1204', '1304', '1404', '1504', '1604', '1804',
        '1904', '1A04', '1B04', '1C04', '1D04', '1E04', '1F04', '2004', '2104',
        '2204', '2404', '2504', '2604', '2704', '2804', '2904', '2A04', '2E04',
        '3004', '3104', '3204', '3304', '3404', '3504', '3604', '3704', '3804',
        '3904', '3A04', '3B04', '3D04', '3E04')
# Номера структур данных формата STLV.
structs = ('2304', '2F04', '2B04', '2C04', '2D04', '3C04', '1704', '0804', '0904')
# Команды ФН
msg_start = '04'
commands = ('02', '03', '04', '05', '06', '07', '10', '11', '12', '13', '14', '15',
            '16', '30', '31', '32', '33', '35')


# Вывод справки
def show_help():
    message = """
                Usage:
                python {0} [src_file] [dst_file]
              """
    print(message.format(sys.argv[0]))


# Приводим строку к порядку следования байтов от старшего к младшему BE.
# Выполняем конвертацию из hex в int.
def toint(string):
    l = re.findall('[0-9a-fA-F]{2}', string)
    l.reverse()
    return int(''.join(l), 16)


# Все тоже самое как и в toint, но первый байт определяет положение дес. точки.
def tofloat(string):
    point = string[:2]
    l = re.findall('[0-9a-fA-F]{2}', string[2:])
    l.reverse()
    return float(int(''.join(l), 16))/(10**int(point))


# Декодируем строку байтов в строку с кодировкой cp 866.
def tocp866(string):
    return string.decode('hex').decode('cp866').encode('utf8')


def todate(string):
    return time.ctime(int(string), 16)


# Основная функция распознавания строки
def parse(string, tags, structs, offset=8, crc=4):
    s = string.replace(' ', '')
    s = s.rstrip()
    s = s[offset:-crc]
    d = {}
    # print(s)
    count = 1
    while(s):
        tag = s[:offset/2]
        length = toint(s[offset/2:offset])
        if tag in structs:
            d[tag] = count, s[offset/2:offset], s[offset:(offset + length*2)]
            s = s[offset:(offset + length*2)]
            count += 1
        elif tag in tags:
            d[tag] = count, s[offset/2:offset], types[tag](s[offset:(offset + length*2)])
            s = s[(offset + length*2):]
            count += 1
        else:
            d[tag] = count, '666', 'ERROR!!! ERROR!!! ERROR!!!'
            break
    return d

# Если при выполнении будет возникать исключение KeyError, то в словарь нужно
# добавить функцию и ключ на который возникло исклЮчение.
# Типы данных:
#     tocp866: ASCII
#     toint: Byte, VLN, int32, int16,
#     tofloat: FVLN
#     todate: UnixTime
types = {
    'FD03': tocp866,
    'FF03': tofloat,
    '0604': tocp866,
    '0704': toint,
    '1304': toint,
    '2804': toint,
    '2904': tocp866,
    '2A04': tocp866,
    '2E04': tofloat,
    '3004': toint,
    '3704': toint,
    '3804': tocp866,
    '3904': toint,
    '2704': tofloat,
    '0B04': toint,
    '1F04': toint
}


if __name__ == "__main__":
    try:
        f_out, f_in = sys.argv[1:]
    except:
        show_help()
        sys.exit()
    print(f_out, f_in)
    with open(f_in, 'w') as fi, open(f_out) as fo:
        for line in fo:
            if line[9:11] == '07':
                res = parse(line, tags, structs)
                fi.write(line)
                for key in sorted(res, key=res.__getitem__):
                    fi.write('{0}|{1}||{3[1]}|{2:>3}|{3[2]}\n'.format(key, toint(key), toint(res[key][1]), res[key]))
            else:
                fi.write(line)
            # time.sleep(1)
