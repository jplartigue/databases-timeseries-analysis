import cProfile
import io
import pstats
import re
from time import time

import pandas as pd

CODE_DIR = '/usr/src/databases_timeseries_analysis/'
EXTERNAL_LIB_DIR = '/opt/venv/lib/python/'


def timer_func(func):
    """
    add a timer to decorated func
    Args:
        func (): function to time
    """
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func


class ProfilerHandler:
    """
    profile performance of code
    see demo_decorator_profiler for usage example
    """
    def __init__(self, print_our_code_only:bool=True, print_callers:bool=False, print_callees:bool=False,
                 sortby:str=None, output_file:str=None, output_table:str=None):
        """
        Args:
            print_our_code_only (): bool : remove external dependancies from report
            print_callers (): add to report "Function xx was called by... xx"
            print_callees (): add to report "Function xx called... xx"
            sortby (): str : sort report table by : 'ncalls' / 'tottime' / 'percall' / 'cumtime' / 'percall'
            output_file (): str/None : if specified, write report to output_file else, print report in console
            output_table (): str/None : if specified, write report table as csv
        """
        # init profile obj
        pr_obj = cProfile.Profile()
        self.pr_obj = pr_obj
        self.print_our_code_only = print_our_code_only
        self.print_callers = print_callers
        self.print_callees = print_callees
        self.sortby = sortby
        self.output_file = output_file
        self.output_table = output_table
        self._logs = ''

    def profile_decorator(self, func):
        """
        profile performance of decorated func
        """
        def wrapper(*args, **kwargs):
            self.pr_obj.enable()
            out = func(*args, **kwargs)
            self.pr_obj.disable()
            return out
        return wrapper

    def profile_func(self, func: callable):
        """
        profile performance of input func
        """
        self.pr_obj = cProfile.Profile()
        self.pr_obj.enable()
        func()
        self.pr_obj.disable()
        return self._gen_report()

    def gen_report(self):
        """
        generate report
        """
        return self._gen_report()

    def _gen_report(self):
        stats_str = self._extract_stats()
        stat_df = self._report_str_to_df(stats_str)
        stat_df = self._clean_stat_df(stat_df)
        self._publish_logs(stat_df)
        return stat_df

    def _log(self, s):
        if self.output_file is None:
            print(s)
        else:
            self._logs += f"\n{s}"

    def _publish_logs(self, stat_df):
        if self.output_file is not None:
            print(f'writting performance profiling file : {self.output_file}')
            with(open(self.output_file, 'w+')) as f:
                f.write(self._logs)
        if self.output_table is not None:
            print(f'writting performance profiling table : {self.output_table}')
            stat_df.to_csv(self.output_table)

    def _extract_stats(self):
        methods_to_apply = []
        if self.print_callers:
            methods_to_apply.append('print_callers')
        if self.print_callees:
            methods_to_apply.append('print_callees')
        for method in methods_to_apply:
            self._log(2 * f'\n{120 * "#"}')
            self._log(f'outputs from {method}')
            self._log(2 * f'{120 * "#"}\n')
            s = io.StringIO()
            ps = pstats.Stats(self.pr_obj, stream=s).strip_dirs().sort_stats('cumulative')
            getattr(ps, method)()
            self._log(s.getvalue())

        s = io.StringIO()
        ps = pstats.Stats(self.pr_obj, stream=s).sort_stats('cumulative')
        ps.print_stats()
        return s.getvalue()

    @staticmethod
    def _report_str_to_df(profile_results):
        """
        transform report_string into a DataFrame
        https://stackoverflow.com/questions/44302726/pandas-how-to-store-cprofile-output-in-a-pandas-dataframe
        """
        ## Parse the stdout text and split it into a table
        data = []
        started = False
        for l in profile_results.split("\n"):
            if not started:
                if l == "   ncalls  tottime  percall  cumtime  percall filename:lineno(function)":
                    started = True
                    data.append(l)
            else:
                data.append(l)
        content = []
        for l in data:
            fs = l.find(" ", 8)
            content.append(
                tuple([l[0:fs], l[fs:fs + 9], l[fs + 9:fs + 18], l[fs + 18:fs + 27], l[fs + 27:fs + 36], l[fs + 36:]]))
        prof_df = pd.DataFrame(content[1:], columns=content[0])
        prof_df.columns = ["ncalls","tottime","percall_tottime","cumtime",'percall_cumtime',"filename:lineno(function)"]
        return prof_df
    

    def _clean_stat_df(self, stat_df):
        """
         - trim printed code if print_our_code_only
         - sort report table using sortby
        """
        col_filename = 'filename:lineno(function)'
        # trim spaces
        stat_df.columns = [re.sub(' ', '', col) for col in stat_df.columns]

        # trim EXTERNAL_LIB_DIR
        stat_df[col_filename] = stat_df[col_filename].apply(lambda row: re.sub(EXTERNAL_LIB_DIR, '../', row))

        print(f'stat_df 1 : {stat_df[:3]}')
        # trim CODE_DIR
        is_our_code = stat_df[col_filename].apply(lambda row: CODE_DIR in row)
        if self.print_our_code_only:
            stat_df = stat_df[is_our_code]
        else:
            stat_df['is_our_code'] = is_our_code
        print(f'stat_df 2  : {stat_df[:3]}')
        # sort
        if self.sortby:
            stat_df.sort_values(by=self.sortby, inplace=True, ascending=False)
        print(f'stat_df 3  : {stat_df[:3]}')
        # log
        self._log(2 * f'\n{120 * "#"}')
        self._log(f'performance report :')
        self._log(2 * f'{120 * "#"}\n')
        self._log(f'{stat_df.to_markdown()}')
        return stat_df

    @staticmethod
    def demo_decorator_profiler():
        """
        usage demonstration
        """
        profiler = ProfilerHandler(print_our_code_only=True, sortby='cumtime', print_callers=True,
                                   output_file='demo_decorator_profiler_output.txt')

        @profiler.profile_decorator
        def _profiled(a, b):
            return a*b+2

        def _not_profiled1(a):
            return 2*a

        def _full_process():
            for i in range(0, 5):
                a=i
                b=2*i
                a=_not_profiled1(a)
                c=_profiled(a,b)

        # usage with profile_decorator
        _full_process()
        profiler.gen_report()

        # # usage with profile_func
        # profiler.profile_func(_full_process_profiled)
        # profiler.gen_report()


# profiler_obj = ProfilerHandler(print_our_code_only=False, sortby='cumtime',
#                                print_callers=True, print_callees=True,
#                                output_file=f'./tmp/perf_output_extcode{dt.datetime.now()}.txt',
#                                output_table=f'./tmp/perf_table_extcode{dt.datetime.now()}.csv')