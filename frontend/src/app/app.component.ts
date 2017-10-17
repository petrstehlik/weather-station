import { Component, OnInit } from '@angular/core';

declare const Dygraph;
declare const io;

const temp = [
    [new Date(1504869255000), 23.1,],
    [new Date(1504868952000), 23.1,],
    [new Date(1504868649000), 23.1,],
    [new Date(1504868347000), 23.1,],
    [new Date(1504868044000), 23.2,],
    [new Date(1504867741000), 23.2,],
    [new Date(1504867438000), 23.2,],
    [new Date(1504867136000), 23.2,],
    [new Date(1504866833000), 23.2,],
    [new Date(1504866530000), 23.2,],
    [new Date(1504866228000), 23.2,],
    [new Date(1504865925000), 23.3,],
    [new Date(1504865622000), 23.3,],
    [new Date(1504865319000), 23.3,],
    [new Date(1504865017000), 23.3,],
    [new Date(1504864714000), 23.3,],
    [new Date(1504864411000), 23.4,],
    [new Date(1504864108000), 23.4,],
    [new Date(1504863806000), 23.4,],
    [new Date(1504863503000), 23.4,]
];

@Component({
  selector: 'app-root',
  template: `
    <h1>
      Weather Station
    </h1>

    <div class="grid">
        <ex-graph
            class="col"
            height="100"
            [labels]="['Temperature', 'Value']"
            [data]="tempData"
            [loading]="tempReady"
            range="null"
            topTitle="Temperature"
        ></ex-graph>
        <div class="col">
            {{ tempData['data'][tempData['data'].length -1] }}
        </div>
    </div>

    <div class="grid">
        <ex-graph
            class="col"
            height="100"
            [labels]="['Temperature', 'Value']"
            [data]="tempData"
            [loading]="tempReady"
            range="null"
            topTitle="Temperature"
        ></ex-graph>
        <div class="col"></div>

    </div>

  `,
  styles: []
})
export class AppComponent implements OnInit {
    tempData : Object = {'data' : [], 'labels' : []};
    tempReady = true;

    ws;

    ngOnInit() {
        this.setData();
        this.ws = io('/ws', { reconnection: true });

        this.ws.on('connect', this.connect);
    }

    public setData() {
        this.tempData['data'] = temp;
        this.tempData['labels'] = ['Temperature', 'Value']
        this.tempReady = false;
    }

    private connect() {
        console.debug("Successfully connected to WS")
    }
}
