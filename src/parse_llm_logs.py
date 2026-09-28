import json
import sys

def parse_logs(file): 
    data = []
    cnt_lines = 0
    cnt_filter_records = 0
    threshold = 1000
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                if (line.strip()):
                    res_dict = json.loads(line)
                    cnt_lines += 1
                    if res_dict.get('tokens_used') and res_dict['tokens_used'] > 1000:
                        data.append(res_dict)
                        cnt_filter_records += 1
            except json.JSONDecodeError:
                sys.stderr.write("json поврежден")
                sys.exit(1) 
        if cnt_lines == 0:
            sys.stderr.write("файл пустой")
            sys.exit(1)
    print(cnt_lines, cnt_filter_records, threshold)
    return data

def write_to_file(records, output_file):
    with open (output_file, "w", encoding="utf-8")as f:
        for record in records:
            json_string = json.dumps(record, ensure_ascii=False)
            f.write(json_string + '\n')
            
final_records = parse_logs("/home/ergei/AIE2_JSON_Logs_Parser_ID_1578120-1/src/data/logs.json")
write_to_file(final_records, "results/filtered_logs.json")