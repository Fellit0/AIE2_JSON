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
                    if not isinstance(res_dict, dict):
                        sys.stderr.write('Строка не является словарем')
                        continue
                    tokens = res_dict.get("tokens_used")
                    latency = res_dict.get("latency_ms")
                    if tokens is not None:
                        if not isinstance(tokens, int):
                            sys.stderr.write('tokens_used не число')
                            continue
                    if latency is not None:
                        if not isinstance(latency, int):
                            sys.stderr.write('latency_ms не число')
                            continue
                    cnt_lines += 1
                    if tokens and res_dict['tokens_used'] > 1000:
                        data.append(res_dict)
                        cnt_filter_records += 1
            except json.JSONDecodeError:
                sys.stderr.write("json поврежден")
                sys.exit(1) 
        if cnt_lines == 0:
            sys.stderr.write("файл пустой")
            sys.exit(1)
    print(cnt_lines, cnt_filter_records, threshold)
    return data, cnt_lines, cnt_filter_records, threshold

def write_to_file(records, output_file):
    with open (output_file, "w", encoding="utf-8")as f:
        for record in records:
            json_string = json.dumps(record, ensure_ascii=False)
            f.write(json_string + '\n')

def calculation_metrics(final_records):
    latency_cnt = 0
    total_tokens = 0
    sum_latency_ms = 0
    median_list = []
    if len(final_records) == 0:
        return 0, 0, 0
    for record in final_records:
        total_tokens = total_tokens + record['tokens_used']
        if record.get('latency_ms'):
            sum_latency_ms = sum_latency_ms + record['latency_ms']
            latency_cnt += 1
            median_list.append(record['latency_ms'])
    if latency_cnt > 0:
        avg_latency_ms = sum_latency_ms / latency_cnt
        median_list.sort()  
        mid = len(median_list) // 2
        if len(median_list) % 2 == 0:
            median = sum(median_list[mid-1:mid+1])/ 2
        else:
            median = median_list[mid]
    else:
        avg_latency_ms = 0
        median = 0
    return total_tokens, avg_latency_ms, median

def report_json(cnt_lines, cnt_filter_records, threshold, total_tokens, avg_latency_ms, latency_metric, file_report):
    json_file = {
        "total_entries": cnt_lines,
        "filtered_entries": cnt_filter_records,
        "token_threshold": threshold,
        "total_tokens": total_tokens,
        "avg_latency_ms": avg_latency_ms,
        "extra_latency_metric": {"name": "median_latency_ms", "value": latency_metric}
    }
    
    with open(file_report, "w", encoding="utf-8") as f:
        json.dump(json_file, f, ensure_ascii=False, indent=4)

final_records, cnt_lines, cnt_filter_records, threshold = parse_logs("data/logs.json")
total_tokens, avg_latency_ms, latency_metric = calculation_metrics(final_records)
write_to_file(final_records, "results/filtered_logs.json")
report_json(
    cnt_lines,
    cnt_filter_records,
    threshold,
    total_tokens,
    avg_latency_ms,
    latency_metric,
    "results/report.json"
)

