"""Flask app factory and routes for the productivity dashboard."""

import datetime
import logging

from flask import Flask, redirect, render_template, request, jsonify

from . import log_parser, analytics, charts
from .monitor import WasteMonitor

LOG_DIR = log_parser.DEFAULT_LOG_DIR


def create_app(start_monitor: bool = True) -> Flask:
    app = Flask(__name__)
    app.config['LOG_DIR'] = LOG_DIR

    if start_monitor:
        monitor = WasteMonitor(log_dir=LOG_DIR)
        monitor.start()
        app.extensions['waste_monitor'] = monitor

    @app.route('/')
    def index():
        return redirect('/today')

    @app.route('/today')
    def today():
        df = log_parser.get_today_log(app.config['LOG_DIR'])
        today_date = datetime.date.today()

        if df is None or df.empty:
            return render_template('today.html',
                                   date=today_date,
                                   bar_json='null',
                                   timeline_json='null',
                                   has_data=False,
                                   stats={})

        sessions = analytics.process_day(df, today_date)
        daily_agg = analytics.aggregate_daily(sessions)

        # Build stats
        stats = {}
        for act_type in ['deep_work', 'light_work', 'wasted']:
            subset = daily_agg[daily_agg['Activity_Type'] == act_type]
            stats[act_type] = subset['DurationHours'].sum() if not subset.empty else 0

        bar_json = charts.today_breakdown_bar(daily_agg)
        timeline_json = charts.today_timeline(sessions)

        return render_template('today.html',
                               date=today_date,
                               bar_json=bar_json,
                               timeline_json=timeline_json,
                               has_data=True,
                               stats=stats)

    @app.route('/range')
    def range_view():
        end_str = request.args.get('end', datetime.date.today().isoformat())
        start_str = request.args.get('start',
            (datetime.date.today() - datetime.timedelta(days=18)).isoformat())

        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()

        file_dict = log_parser.get_raw_files(
            app.config['LOG_DIR'], date_range=(start_date, end_date))

        if not file_dict:
            return render_template('range.html',
                                   start=start_str, end=end_str,
                                   bar_json='null', trend_json='null',
                                   has_data=False)

        sessions = analytics.process_range(file_dict, log_parser.read_raw_log)
        daily_agg = analytics.aggregate_daily(sessions)

        bar_json = charts.range_stacked_bar(daily_agg)
        trend_json = charts.range_trend_lines(daily_agg)

        return render_template('range.html',
                               start=start_str, end=end_str,
                               bar_json=bar_json, trend_json=trend_json,
                               has_data=True)

    @app.route('/summary')
    def summary():
        end_str = request.args.get('end', datetime.date.today().isoformat())
        start_str = request.args.get('start',
            (datetime.date.today() - datetime.timedelta(days=18)).isoformat())

        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()

        file_dict = log_parser.get_raw_files(
            app.config['LOG_DIR'], date_range=(start_date, end_date))

        if not file_dict:
            return render_template('summary.html',
                                   start=start_str, end=end_str,
                                   pie_json='null',
                                   has_data=False, stats={}, num_days=0)

        sessions = analytics.process_range(file_dict, log_parser.read_raw_log)
        total_agg = analytics.aggregate_total(sessions)
        daily_agg = analytics.aggregate_daily(sessions)

        # Per-day averages
        num_days = daily_agg['Date'].nunique() if not daily_agg.empty else 1
        stats = {}
        for _, row in total_agg.iterrows():
            stats[row['Activity_Type']] = {
                'total': row['TotalHours'],
                'avg': row['TotalHours'] / num_days,
                'sessions': int(row['SessionCount']),
            }

        pie_json = charts.summary_pie(total_agg)

        return render_template('summary.html',
                               start=start_str, end=end_str,
                               pie_json=pie_json,
                               has_data=True,
                               stats=stats,
                               num_days=num_days)

    @app.route('/api/today')
    def api_today():
        df = log_parser.get_today_log(app.config['LOG_DIR'])
        today_date = datetime.date.today()

        if df is None or df.empty:
            return jsonify({'has_data': False, 'date': today_date.isoformat()})

        sessions = analytics.process_day(df, today_date)
        daily_agg = analytics.aggregate_daily(sessions)

        stats = {}
        for act_type in ['deep_work', 'light_work', 'wasted']:
            subset = daily_agg[daily_agg['Activity_Type'] == act_type]
            stats[act_type] = round(
                subset['DurationHours'].sum() if not subset.empty else 0, 2)

        return jsonify({
            'has_data': True,
            'date': today_date.isoformat(),
            'stats': stats,
        })

    return app


def main():
    logging.basicConfig(level=logging.INFO)
    app = create_app(start_monitor=True)
    app.run(host='127.0.0.1', port=5050, debug=False)


if __name__ == '__main__':
    main()
