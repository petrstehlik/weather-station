declare const Dygraph;

import { Component, OnInit, Input, ViewChild, ElementRef, OnChanges, SimpleChanges } from '@angular/core';
import { environment as env } from 'environments/environment';

@Component({
  selector: 'ex-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})
export class GraphComponent implements OnInit, OnChanges {

    /**
     * Data to render in the graph
     *
     * The data item is expected to have the first item in array a Date object
     *
     * format: {
     *      "labels" : [],
     *      "data" : []
     * }
     */
    private _data: Object;
    private graphRef;
    private config;

    ngOnChanges(changes: SimpleChanges): void {
        if (changes) {
            if (this._data != undefined && Object.keys(this._data).length !== 0) {
                this.update()
            }
        }
    }

    @Input()
    set data(data) {
        if (this.config == undefined) {
            this.initConfig();
        }

        if (data != undefined && Object.keys(data).length !== 0) {
            this._data = data;
            this.update()
        }
    }

    get data() {
        return this._data;
    }

    @Input('loading') loading: boolean;

    @Input() topTitle = 'Untitled Chart';
    @Input() labels = ['Date'];
    @Input() labelY = 'Untitled Y axis';

    // The trick with 100.5 is to display the 100 tick in the graph
    @Input() range = null;

    // Set height of chart's div so the chart itself will resize to it
    @Input() height = env.chart.height;

    @Input() stacked = false;
    @Input() bar = false;

    @ViewChild('chart') chart: ElementRef;
    @ViewChild('chartLabels') labelsDivRef: ElementRef;

    constructor() { }

    ngOnInit() {
        this.initConfig();
    }

    private initConfig() {
        this.config = {
            //labels : this.labels,
            hideOverlayOnMouseOut : true,
            //ylabel: this.labelY,
            title : "",
            legend: 'follow',
            labelsDiv : this.labelsDivRef.nativeElement,
            highlightCallback : this.moveLabel,
            gridLineColor : 'rgb(242, 242, 242)',
            highlightCircleSize: 2,
            strokeWidth: 1,
            strokeBorderWidth : 1,
            valueRange : this.range,
            stackedGraph : this.stacked,
            plotter : this.bar ? this.barChartPlotter : null,
            rightGap : 0,
            highlightSeriesOpts: {
              strokeWidth: 2,
              strokeBorderWidth: 0,
              highlightCircleSize: 2
            },
            axes : {
                x : {
                    drawAxis : false,
                    drawGrid : false
                },
                y : {
                    drawAxis : false,
                    drawGrid : false
                }
            }
        };
    }

    public update() {
        if (this.graphRef === undefined) {
            this.config['labels'] = this._data['labels'];
            this.graphRef = new Dygraph(
                this.chart.nativeElement,
                this._data['data'],
                this.config);
        } else {
            this.graphRef.updateOptions({
                file : this._data['data'],
                labels : this._data['labels']
            });
        }
    }

    public moveLabel(event, x, points, row, seriesName) {
        // Use event's DOM to find the labels div to operate with
        // This way we can have multiple graphs on the same page
        const label = (event.composedPath())[1].lastChild;

        // Set styles
        label.style.display = 'inline-block';
        label.style.left = (env.chart.labels.offsetX) + 'px';
        label.style.top = (env.chart.labels.offsetY) + 'px';
    }

    private legendFormatter(data): void {
        return data;
    }

    private extractData(raw: Object): Array<any> {
        return raw['queries'][0]['results'][0]['values'];
    }

    // This function draws bars for a single series. See
    // multiColumnBarPlotter below for a plotter which can draw multi-series
    // bar charts.
    private barChartPlotter(e) {
        const ctx = e.drawingContext;
        const points = e.points;
        const y_bottom = e.dygraph.toDomYCoord(0);

        ctx.fillStyle = e.color;

        // Find the minimum separation between x-values.
        // This determines the bar width.
        let min_sep = Infinity;
        for (let i = 1; i < points.length; i++) {
          const sep = points[i].canvasx - points[i - 1].canvasx;
          if (sep < min_sep) min_sep = sep;
        }
        const bar_width = Math.floor(2.0 / 3 * min_sep);

        // Do the actual plotting.
        for (let i = 0; i < points.length; i++) {
          const p = points[i];
          const center_x = p.canvasx;

          ctx.fillRect(center_x - bar_width / 2, p.canvasy,
              bar_width, y_bottom - p.canvasy);

          ctx.strokeRect(center_x - bar_width / 2, p.canvasy,
              bar_width, y_bottom - p.canvasy);
        }
    }
}
