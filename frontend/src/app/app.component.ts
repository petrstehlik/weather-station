import { Component, OnInit } from '@angular/core';

declare const Dygraph;
declare const io;

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
  `,
  styles: []
})
export class AppComponent implements OnInit {
    tempData : Object = {'data' : [], 'labels' : []};
    tempLoad = true;

    ws;
    data : Object = {
        temperature : undefined
    };

    ngOnInit() {
        this.ws = io('/ws', { reconnection: true });

        this.ws.on('connect', () => {
            console.debug("Successfully connected to WS")
        });

        this.ws.on('init', (data) => {
            this.data = JSON.parse(data);
            this.parseData();
        });

        this.ws.on('data', (data) => {
            this.data['temperature'].push_back([new Date(data['temperature'][0]), data['temperature'][1]]);
            this.data['humidity'].push_back([new Date(data['humidity'][0]), data['humidity'][1]]);
            this.data['pressure'].push_back([new Date(data['pressure'][0]), data['pressure'][1]]);
        });
    }

    private parseData() {
        for (let item of this.data['temperature'] ) {
            item[0] = new Date(item[0])
        }

        for (let item of this.data['humidity'] ) {
            item[0] = new Date(item[0])
        }

        for (let item of this.data['pressure'] ) {
            item[0] = new Date(item[0])
        }

        console.log(this.data)
        this.data["temperature"] = {
            "labels" : ['Temperature', 'Value'],
            "data" : this.data["temperature"]
        }

        this.data["pressure"] = {
            "labels" : ['Temperature', 'Value'],
            "data" : this.data["pressure"]
        }

        this.data["humidity"] = {
            "labels" : ['Temperature', 'Value'],
            "data" : this.data["humidity"]
        }
        this.tempLoad = false;
    }

}
