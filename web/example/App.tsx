import * as React from 'react';
import { Button, Container, Statistic, Form, Divider, Checkbox, Segment } from 'semantic-ui-react';

import Recorder from '../src/index';
const lamejs = require('lamejs')

import { encodeWAV } from '../src/transform/transform';
import Player from '../src/player/player';


import 'semantic-ui-css/semantic.min.css';
import axios from 'axios';



declare let OggVorbisEncoder: any;

let recorder = null;
let playTimer = null;
let oCanvas = null;
let ctx = null;
let drawRecordId = null;
let pCanvas = null;
let pCtx = null;
let drawPlayId = null;
let startStatus = false;
let originalTime = 0;
let list = [];
let data = {};
let len = 0;
const sampleRateOptions = [
    { text: '8000', value: 8000 },
    { text: '16000', value: 16000 },
    { text: '22050', value: 22050 },
    { text: '24000', value: 24000 },
    { text: '44100', value: 44100 },
    { text: '48000', value: 48000 },
];

const sampleBitOptions = [
    { text: '8', value: 8 },
    { text: '16', value: 16 },
];

const numChannelOptions = [
    { text: 'Single', value: 1 },
    { text: 'Double', value: 2 },
];

// 定时获取录音文件播放了多少
// setInterval(() => {
//     recorder && recorder.getPlayTime() && console.log('已经播放了:', recorder.getPlayTime());
// }, 300)

// Recorder.getPermission().then(() => {
//     console.log('给权限了');
// }, (error) => {
//     console.log(`${error.name} : ${error.message}`);
// });
document.onkeydown = (e) => {
    onKeyPress();
}

function onKeyPress() {
    len += 1;
    if( startStatus){
        var pressTime = new Date().getTime();
        var e = window.event || e;
        var keyCode = e.keyCode;
        var obj = {
          time: pressTime - originalTime,
          charCode: keyCode
        }
        list.push(obj);
        // mapKeyPressToActualCharacter(event.shiftKey, keyCode);
        console.log(list);
    }
}

class App extends React.Component {
    state = {
        sampleBit: 16,
        sampleRate: 16000,
        numChannel: 1,
        compiling: false,
        recordForTest: false,
        isRecording: false,     // 是否正在录音
        duration: 0,
        fileSize: 0,
        vol: 0,
    }
    changeSampleRate = (e, params) => {
        this.setState({
            sampleRate: params.value
        });
    }
    changeSampleBit = (e, params) => {
        this.setState({
            sampleBit: params.value
        });
    }
    changeNumChannel = (e, params) => {
        this.setState({
            numChannel: params.value
        });
    }
    changeCompile = (e, { checked }) => {
        this.setState({
            recordForTest: checked
        });
      }

    collectData = () => {
        return {
            sampleBits: this.state.sampleBit,
            sampleRate: this.state.sampleRate,
            numChannels: this.state.numChannel,
            compiling: this.state.compiling,       // 是否开启边录音边转化（后期改用web worker）
        };
    }

    modifyOption = () => {
        if (recorder) {
            const config = this.collectData();

            recorder.setOption(config);

            recorder = null;
        }
    }

    jumpToMLOperation = () => {
        location.href = "http://8f13-2601-180-8300-5760-c019-f247-c79-f57.ngrok.io/train/index"
    }

    startRecord = () => {
        startStatus = true;
        originalTime = new Date().getTime();
        this.clearPlay();

        const config = this.collectData();

        if (!recorder) {
            recorder = new Recorder(config);

            recorder.onprocess = function(duration) {
                // this.setState({
                //     duration: duration.toFixed(5),
                // });
                // 推荐使用 onprogress
            }

            recorder.onprogress = (params) => {
                // console.log(recorder.duration);
                // console.log(recorder.fileSize);

                this.setState({
                    duration: params.duration.toFixed(5),
                    fileSize: params.fileSize,
                    vol: params.vol.toFixed(2)
                });
                // 此处控制数据的收集频率
                if (config.compiling) {
                    console.log('音频总数据：', params.data);
                }
            }

            recorder.onplay = () => {
                console.log('%c回调监听，开始播放音频', 'color: #2196f3')
            }
            recorder.onpauseplay = () => {
                console.log('%c回调监听，暂停播放音频', 'color: #2196f3')
            }
            recorder.onresumeplay = () => {
                console.log('%c回调监听，恢复播放音频', 'color: #2196f3')
            }
            recorder.onstopplay = () => {
                console.log('%c回调监听，停止播放音频', 'color: #2196f3')
            }
            recorder.onplayend = () => {
                console.log('%c回调监听，音频已经完成播放', 'color: #2196f3')
                // 播放结束后，停止绘制canavs
                this.stopDrawPlay();
            }

            // 定时获取录音的数据并播放
            config.compiling && (playTimer = setInterval(() => {
                if (!recorder) {
                    return;
                }

                let newData = recorder.getNextData();
                if (!newData.length) {
                    return;
                }
                let byteLength = newData[0].byteLength
                let buffer = new ArrayBuffer(newData.length * byteLength)
                let dataView = new DataView(buffer)

                    // 数据合并
                for (let i = 0, iLen = newData.length; i < iLen; ++i) {
                    for (let j = 0, jLen = newData[i].byteLength; j < jLen; ++j) {
                        dataView.setInt8(i * byteLength + j, newData[i].getInt8(j))
                    }
                }

                // 将录音数据转成WAV格式，并播放
                let a = encodeWAV(dataView, config.sampleRate, config.sampleRate, config.numChannels, config.sampleBits)
                let blob: any = new Blob([ a ], { type: 'audio/wav' });

                blob.arrayBuffer().then((arraybuffer) => {
                    Player.play(arraybuffer);
                });
            }, 3000))
        } else {
            recorder.stop();
        }

        recorder.start().then(() => {
            console.log('开始录音');
        }, (error) => {
            console.log(`异常了,${error.name}:${error.message}`);
        });
        // 开始绘制canvas
        this.drawRecord();
    }

    drawRecord = () => {
        // 用requestAnimationFrame稳定60fps绘制
        drawRecordId = requestAnimationFrame(this.drawRecord);

        // 实时获取音频大小数据
        let dataArray = recorder.getRecordAnalyseData(),
            bufferLength = dataArray.length;

        // 填充背景色
        ctx.fillStyle = 'rgb(200, 200, 200)';
        ctx.fillRect(0, 0, oCanvas.width, oCanvas.height);

        // 设定波形绘制颜色
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'rgb(0, 0, 0)';

        ctx.beginPath();

        var sliceWidth = oCanvas.width * 1.0 / bufferLength, // 一个点占多少位置，共有bufferLength个点要绘制
            x = 0;          // 绘制点的x轴位置

        for (var i = 0; i < bufferLength; i++) {
            var v = dataArray[i] / 128.0;
            var y = v * oCanvas.height / 2;

            if (i === 0) {
                // 第一个点
                ctx.moveTo(x, y);
            } else {
                // 剩余的点
                ctx.lineTo(x, y);
            }
            // 依次平移，绘制所有点
            x += sliceWidth;
        }

        ctx.lineTo(oCanvas.width, oCanvas.height / 2);
        ctx.stroke();
    }

    drawPlay = () => {
        // 用requestAnimationFrame稳定60fps绘制
        drawPlayId = requestAnimationFrame(this.drawPlay);

        // 实时获取音频大小数据
        let dataArray = recorder.getPlayAnalyseData(),
            bufferLength = dataArray.length;

        // 填充背景色
        pCtx.fillStyle = 'rgb(200, 200, 200)';
        pCtx.fillRect(0, 0, pCanvas.width, pCanvas.height);

        // 设定波形绘制颜色
        pCtx.lineWidth = 2;
        pCtx.strokeStyle = 'rgb(0, 0, 0)';

        pCtx.beginPath();

        var sliceWidth = pCanvas.width * 1.0 / bufferLength, // 一个点占多少位置，共有bufferLength个点要绘制
            x = 0;          // 绘制点的x轴位置

        for (var i = 0; i < bufferLength; i++) {
            var v = dataArray[i] / 128.0;
            var y = v * pCanvas.height / 2;

            if (i === 0) {
                // 第一个点
                pCtx.moveTo(x, y);
            } else {
                // 剩余的点
                pCtx.lineTo(x, y);
            }
            // 依次平移，绘制所有点
            x += sliceWidth;
        }

        pCtx.lineTo(pCanvas.width, pCanvas.height / 2);
        pCtx.stroke();
    }

    pauseRecord = () => {
        if (recorder) {
            recorder.pause();
            console.log('暂停录音');
            drawRecordId && cancelAnimationFrame(drawRecordId);
            drawRecordId = null;
        }
    }
    resumeRecord = () => {
        recorder && recorder.resume();
        console.log('恢复录音');
        this.drawRecord();
    }
    endRecord = () => {
        if(recorder){
            let fd = new FormData();
            var blob = recorder.getWAVBlob();
            fd.append("wavFile", blob);
            fd.append("chars", JSON.stringify(list));
            fd.append("length",JSON.stringify(len));
            fd.append("isTestData", JSON.stringify(this.state.recordForTest))
            console.log(fd.get('chars'));
            data= {
                isTestData : this.state.recordForTest,
                wav : fd,
                chars: list,
                length: len
            }
            let url = 'http://8f13-2601-180-8300-5760-c019-f247-c79-f57.ngrok.io/api/audioCharPairsAPI';
            axios.post(url,fd,{headers: {'content-type': 'multipart/form-data'}})
            .then((response) => {
                alert(response.data.message)
            })
            .catch((error) => {

            })

        }
        recorder && recorder.stop();
        console.log('结束录音');
        drawRecordId && cancelAnimationFrame(drawRecordId);
        drawRecordId = null;
        startStatus = false;
        list = [];
        len = 0;
    }
    playRecord = () => {
        recorder && recorder.play();
        drawRecordId && cancelAnimationFrame(drawRecordId);
        drawRecordId = null;
        console.log('播放录音');
        recorder && this.drawPlay();
        // setInterval(() => {
        //     recorder.getPlayTime()
        // }, 500)
    }
    pausePlay = () => {
        this.stopDrawPlay();
        recorder && recorder.pausePlay();
        console.log('暂停播放');
    }
    resumePlay = () => {
        recorder && recorder.resumePlay();
        console.log('恢复播放');
        this.drawPlay();
    }
    clearPlay = () => {
        if (playTimer) {
            clearInterval(playTimer);
            playTimer = null;
        }
        if (drawRecordId) {
            cancelAnimationFrame(drawRecordId);
            drawRecordId = null;
        }
        this.stopDrawPlay();
    }
    stopDrawPlay= () => {
        drawPlayId && cancelAnimationFrame(drawPlayId);
        drawPlayId = null;
    }
    stopPlay = () => {
        this.clearPlay();
        recorder && recorder.stopPlay();
        console.log('停止播放');
        this.stopDrawPlay();
    }
    destroyRecord = () => {
        this.clearPlay();
        if (recorder) {
            recorder.destroy().then(() => {
                console.log('销毁实例');
                recorder = null;
                drawRecordId && cancelAnimationFrame(drawRecordId);
                this.stopDrawPlay();
            });
        }
    }
    downloadPCM = () => {
        if (recorder) {
            console.log('pcm: ', recorder.getPCMBlob());
            recorder.downloadPCM();
        }
    }
    downloadWAV = () => {
        if (recorder) {
            console.log('wav: ', recorder.getWAVBlob());
            recorder.downloadWAV();
        }
    }

    playMP3 = () => {
        if (recorder) {
            const mp3Blob = convertToMp3(recorder.getWAV());
            const reader = new FileReader();

            reader.onload = function() {
                Player.play(this.result);
            }

            reader.readAsArrayBuffer(mp3Blob)

            console.log(mp3Blob);
        }
    }

    downloadMP3 = () => {
        if (recorder) {
            const mp3Blob = convertToMp3(recorder.getWAV());

            recorder.download(mp3Blob, 'recorder', 'mp3');
        }
    }

    // playOGG = () => {
    //     if (recorder) {
    //         const mp3Blob = convertToMp3(recorder.getWAV());
    //         const oggBlob = convertToOgg(mp3Blob);
    //         const reader = new FileReader();

    //         reader.onload = function() {
    //             Player.play(this.result);
    //         }

    //         reader.readAsArrayBuffer(oggBlob)
    //         console.log(oggBlob)
    //         // recorder.download(oggBlob, 'recorder', 'ogg');
    //     }
    // }
    // downloadOGG = () => {}

    uploadAudio = (e) => {
        e.target.files[0].arrayBuffer().then((arraybuffer) => {
            Player.play(arraybuffer);
        });
    }

    componentDidMount() {
        oCanvas = document.getElementById('canvas');
        ctx = oCanvas.getContext("2d");
        pCanvas = document.getElementById('playChart');
        pCtx = pCanvas.getContext("2d");
    }

    public render() {
        return (
            <Container className="App" style={{ margin: '20px 0' }}>
                <Form>
                    <Form.Group widths='equal'>
                        <Form.Select
                            fluid
                            label='Sampling Rate'
                            value={ this.state.sampleRate }
                            options={ sampleRateOptions }
                            onChange={ this.changeSampleRate }
                        />
                        <Form.Select
                            fluid
                            label='Sampling bits'
                            value={ this.state.sampleBit }
                            options={ sampleBitOptions }
                            onChange={ this.changeSampleBit }
                        />
                        <Form.Select
                            fluid
                            label='Track number'
                            value={ this.state.numChannel }
                            options={ numChannelOptions }
                            onChange={ this.changeNumChannel }
                        />
                    </Form.Group>
                    <Form.Field>
                        <Checkbox label='Record for test' checked={ this.state.recordForTest } toggle onChange={ this.changeCompile } />
                    </Form.Field>
                </Form>
                <Divider />
                <div>
                    <Button primary onClick={ this.modifyOption }>
                        Reset Configuration
                    </Button>
                    <Button primary onClick={ this.jumpToMLOperation }>
                        Train/Test
                    </Button>
                </div>
                <Divider />
                <div>
                    <Button primary onClick={ this.startRecord }>
                        Start Recording
                    </Button>
                    <Button primary onClick={ this.pauseRecord }>
                        Pause Recording
                    </Button>
                    <Button primary onClick={ this.resumeRecord }>
                        Resume Recording
                    </Button>
                    <Button primary onClick={ this.endRecord }>
                        Stop Recording
                    </Button>
                </div>
                <Divider />
                <Statistic.Group widths='three'>
                    <Statistic>
                        <Statistic.Value>{ this.state.duration }</Statistic.Value>
                        <Statistic.Label>Length of recording(sec)</Statistic.Label>
                    </Statistic>
                    <Statistic>
                        <Statistic.Value>{ this.state.fileSize }</Statistic.Value>
                        <Statistic.Label>Length of recording(bytes)</Statistic.Label>
                    </Statistic>
                    <Statistic>
                        <Statistic.Value>{ this.state.vol }</Statistic.Value>
                        <Statistic.Label>Percentage of current recording volume(%)</Statistic.Label>
                    </Statistic>
                </Statistic.Group>
                <div>
                    <span>Recording：</span>
                    <canvas id="canvas"></canvas>
                    <span>Play：</span>
                    <canvas id="playChart"></canvas>
                </div>
                <Divider />
                <div>
                    <Button onClick={ this.playRecord }>
                        Play Recording
                    </Button>
                    <Button onClick={ this.pausePlay }>
                        Pause Playing
                    </Button>
                    <Button onClick={ this.resumePlay }>
                        Resume Playing
                    </Button>
                    <Button onClick={ this.stopPlay }>
                        Stop Playing
                    </Button>
                    <Button onClick={ this.destroyRecord }>
                        Destroy instance
                    </Button>
                </div>
                <Divider />
                <div>
                    <h3>Download</h3>
                    <Button onClick={ this.downloadPCM } secondary>
                        Download as PCM
                    </Button>
                    <Button onClick={ this.downloadWAV } secondary>
                        Download as WAV
                    </Button>
                </div>
                <Divider />
                <div>
                    <h3>Other Audio Formats</h3>
                    <h4>MP3</h4>
                    <Button onClick={ this.playMP3 } secondary>
                        Play as MP3
                    </Button>
                    <Button onClick={ this.downloadMP3 } secondary>
                        download as MP3
                    </Button>

                    {/* <h4>OGG</h4>
                    <Button onClick={ this.playOGG } secondary>
                        播放OGG
                    </Button>
                    <Button onClick={ this.downloadOGG } secondary>
                        下载OGG
                    </Button> */}
                </div>
                <Divider />
            </Container>
        );
    }
}

// https://github.com/2fps/recorder/issues/33 支持mp3
// 请用 16位的采样位数
function convertToMp3(wavDataView) {
    // 获取wav头信息
    const wav = lamejs.WavHeader.readHeader(wavDataView); // 此处其实可以不用去读wav头信息，毕竟有对应的config配置
    const { channels, sampleRate } = wav;
    console.log('wav', wav)
    const mp3enc = new lamejs.Mp3Encoder(channels, sampleRate, 128);
    // 获取左右通道数据
    const result = recorder.getChannelData()
    const buffer = [];

    const leftData = result.left && new Int16Array(result.left.buffer, 0, result.left.byteLength / 2);
    const rightData = result.right && new Int16Array(result.right.buffer, 0, result.right.byteLength / 2);
    const remaining = leftData.length + (rightData ? rightData.length : 0);

    const maxSamples = 1152;
    for (let i = 0; i < remaining; i += maxSamples) {
        const left = leftData.subarray(i, i + maxSamples);
        let right = null;
        let mp3buf = null;

        if (channels === 2) {
            right = rightData.subarray(i, i + maxSamples);
            mp3buf = mp3enc.encodeBuffer(left, right);
        } else {
            mp3buf = mp3enc.encodeBuffer(left);
        }

        if (mp3buf.length > 0) {
            buffer.push(mp3buf);
        }
    }

    const enc = mp3enc.flush();

    if (enc.length > 0) {
        buffer.push(enc);
    }

    return new Blob(buffer, { type: 'audio/mp3' });
}

// function convertToOgg(mp3Blob) {
//     // var encoder = new OggVorbisEncoder(16000, 1)

//     const result = recorder.getChannelData()
//     // const leftData = new Float32Array(result.left.buffer, 0, result.left.byteLength / 4)
//     // // const rightData = new Float32Array(result.right.buffer, 0, result.right.byteLength / 4)
//     // encoder.encode([leftData])

//     // const blob = encoder.finish()

//     // return blob
// }

export default App;
