import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  template: `
    <h1>
      Weather Station
    </h1>

    <div class="grid">
        <div class="col">
            <ex-graph
                height="100"
                [labels]="['Temperature', 'Value']"
                [data]="data?.temperature"
                [loading]="tempLoad"
                range="null"
                topTitle="Temperature"
                labelY="null"
            ></ex-graph>
        </div>
        <div class="col big-num" *ngIf="!tempLoad">
            {{ data?.temperature?.data[data?.temperature?.data.length-1][1] }} °C
        </div>

    </div>

    <div class="grid">
        <div class="col">
            <ex-graph
                height="100"
                [labels]="['Pressure', 'Value']"
                [data]="data?.pressure"
                [loading]="tempLoad"
                range="null"
                topTitle="Pressure"
                labelY="null"
            ></ex-graph>
        </div>
        <div class="col big-num" *ngIf="!tempLoad">
            {{ data?.pressure?.data[data?.pressure?.data.length-1][1] / 100 }} hPa
        </div>

    </div>

    <div class="grid">
        <div class="col">
            <ex-graph
                height="100"
                [labels]="['Humidity', 'Value']"
                [data]="data?.humidity"
                [loading]="tempLoad"
                range="null"
                topTitle="Humidity"
                labelY="null"
            ></ex-graph>
        </div>
        <div class="col big-num" *ngIf="!tempLoad">
            {{ data?.humidity?.data[data?.humidity?.data.length-1][1] }} %
        </div>

    </div>

     <div class="grid">
        <div class="col">
            <ex-graph
                height="100"
                [labels]="['Light', 'Value']"
                [data]="data?.light"
                [loading]="tempLoad"
                range="null"
                topTitle="Light"
                labelY="null"
            ></ex-graph>
        </div>
        <div class="col big-num" *ngIf="!tempLoad">
            {{ data?.light?.data[data?.light?.data.length-1][1] }} %
        </div>

    </div>

     <div class="grid">
        <div class="col">
            <ex-graph
                height="100"
                [labels]="['Moisture', 'Value']"
                [data]="data?.moisture"
                [loading]="tempLoad"
                range="null"
                topTitle="Moisture"
                labelY="null"
            ></ex-graph>
        </div>
        <div class="col big-num" *ngIf="!tempLoad">
            {{ data['moisture']['data'][data['moisture']['data'].length-1][1] }} %
        </div>

    </div>


  `,
  styles: [],
  providers : [HttpClient]
})
export class AppComponent implements OnInit {
    tempData : Object = {'data' : [], 'labels' : []};
    tempLoad = true;
    interval = undefined;
    metrics = ['temperature', 'humidity', 'pressure', 'light', 'moisture'];

    ws;
    data : Object = {
        temperature : undefined
    };

    constructor(private http: HttpClient) {}

    ngOnInit() {
        this.http.get('/api/init').subscribe(data => {
            this.data = data;
            this.parseData();
            this.interval = setInterval(() => {
                this.http.get('/api/latest').subscribe(data => {
                    let t = this.data['temperature']["data"]

                    // Don't do anything if we have still old data
                    if (t[t.length - 1][0] == new Date(data['temperature'][0]))
                        return

                    for (let item of this.metrics) {
                        this.data[item]['data'].push([new Date(data[item][0]), data[item][1]]);
                    }
                })
            }, 5000);
        });
    }

    private parseData() {
        for (let metric of this.metrics) {
            for (let item of this.data[metric] ) {
                item[0] = new Date(item[0])
            }

            this.data[metric] = {
                "labels" : [metric, 'Value'],
                "data" : this.data[metric]
            }
        }

        this.tempLoad = false;
    }

}
