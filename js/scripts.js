//initialise global variables
mypen = false;
isClear = false;
strokeColor = "#000000";
eraserSize = 8;
lines = []
linePoints = [];
eraserPointsIndex = [];
pathContent = "";

//HTML element selector
var canvas = document.getElementById("myCanvas");
$(canvas).css("cursor", "crosshair");
var c = canvas.getContext("2d");
svg = d3.select("#mySvg");
var linePath = d3.line();

//Event: when the mouse is down
$("#drawBox").mousedown(function(evt) {
    mypen = true;
    if (!isClear) {
        linePoints = [];
        maxD = 0;
        c.beginPath();
        c.moveTo(evt.offsetX, evt.offsetY);
        linePoints.push([evt.offsetX, evt.offsetY]);
        startPoint = [evt.offsetX, evt.offsetY];
        middlePoint = [evt.offsetX, evt.offsetY];
    } else {
        x = evt.offsetX;
        y = evt.offsetY;
        c.clearRect(x - eraserSize / 2., y - eraserSize / 2., eraserSize, eraserSize);
        for (var i = 0; i < lines.length; i++) {
            lines[i].line.forEach(function(ele, index, a) {
                if (isInEraser(ele, [x, y])) {
                    var hasIt = false;
                    for (var k = 0; k < eraserPointsIndex.length; k++) {
                        if (eraserPointsIndex[k].line == i && eraserPointsIndex[k].point == index) {
                            hasIt = true;
                            break;
                        }
                    }
                    if (!hasIt)
                        eraserPointsIndex.push({
                            line: i,
                            point: index
                        });
                }
            });
        }
    }
});

//Event: mouse movement
$("#drawBox").mousemove(function(evt) {
    if (mypen) {
        if (!isClear) {
            c.lineTo(evt.offsetX, evt.offsetY);
            c.strokeStyle = strokeColor;
            c.stroke();
            linePoints.push([evt.offsetX, evt.offsetY]);
            if (squareDistance([evt.offsetX, evt.offsetY], startPoint) > maxD) {
                maxD = squareDistance([evt.offsetX, evt.offsetY], startPoint);
                middlePoint = [evt.offsetX, evt.offsetY];
            }

        } else {
            x = evt.offsetX;
            y = evt.offsetY;
            c.clearRect(x - eraserSize / 2., y - eraserSize / 2., eraserSize, eraserSize);
            for (var i = 0; i < lines.length; i++) {
                lines[i].line.forEach(function(ele, index, a) {
                    if (isInEraser(ele, [x, y])) {
                        var hasIt = false;
                        for (var k = 0; k < eraserPointsIndex.length; k++) {
                            if (eraserPointsIndex[k].line == i && eraserPointsIndex[k].point == index) {
                                hasIt = true;
                                break;
                            }
                        }
                        if (!hasIt)
                            eraserPointsIndex.push({
                                line: i,
                                point: index
                            });
                    }
                });
            }
        }
    }
});

//Event: the mouse is up
$("#drawBox").mouseup(function(evt) {
    mypen = false;
    if (!isClear) {
        c.lineTo(evt.offsetX, evt.offsetY);
        c.strokeStyle = strokeColor;
        c.stroke();
        linePoints.push([evt.offsetX, evt.offsetY]);
        lines.push({
            line: linePoints,
            diameter: maxD,
            middle: middlePoint
        });
        endPoint = [evt.offsetX, evt.offsetY];
        if (squareDistance(startPoint, endPoint) == 0);
        else if (squareDistance(startPoint, endPoint) < 1 && maxD < 1) {
            svg.append("circle")
                .attr("fill", "none")
                .attr("stroke", strokeColor)
                .attr("stroke-width", "1px")
                .attr("r", "5px")
                .attr("cx", (startPoint[0] + middlePoint[0]) / 2 + "")
                .attr("cy", (startPoint[1] + middlePoint[1]) / 2 + "")
        } else {
            svg.append("path")
                .attr("d", linePath(linePoints))
                .attr("stroke", strokeColor)
                .attr("stroke-width", "2px")
                .attr("fill", "none");

            var content = $("#pathD").val();
            if (content == "")
                var newContent = content + linePath(linePoints)
            else
                var newContent = content + "\n" + linePath(linePoints);
            pathContent = pathContent+"\n"+newContent;
        }
    } else {
        x = evt.offsetX;
        y = evt.offsetY;
        c.clearRect(x - eraserSize / 2., y - eraserSize / 2., eraserSize, eraserSize);
        paths = [];
        for (var i = 0; i < lines.length; i++)
            paths.push("");
        for (var i = 0; i < lines.length; i++) {
            lines[i].line.forEach(function(ele, index, a) {
                if (isInEraser(ele, [x, y])) {
                    var hasIt = false;
                    for (var k = 0; k < eraserPointsIndex.length; k++) {
                        if (eraserPointsIndex[k].line == i && eraserPointsIndex[k].point == index) {
                            hasIt = true;
                            break;
                        }
                    }
                    if (!hasIt)
                        eraserPointsIndex.push({
                            line: i,
                            point: index
                        });
                }
            });
        }
        for (var i = 0; i < lines.length; i++) {
            for (var j = 0; j < lines[i].line.length; j++) {
                var erased = false;
                for (var k = 0; k < eraserPointsIndex.length; k++) {
                    if (eraserPointsIndex[k].line == i && eraserPointsIndex[k].point == j) {
                        erased = true;
                        break;
                    }
                }
                if (erased) {
                    if (j > 0) {
                        x1 = (lines[i].line[j - 1][0] + lines[i].line[j][0]) / 2.;
                        y1 = (lines[i].line[j - 1][1] + lines[i].line[j][1]) / 2.;
                    }
                    if (j < lines[i].line.length - 1) {
                        x2 = (lines[i].line[j][0] + lines[i].line[j + 1][0]) / 2.;
                        y2 = (lines[i].line[j][1] + lines[i].line[j + 1][1]) / 2.;
                    }
                    if (j == 0)
                        paths[i] += "M" + x2 + "," + y2;
                    else if (j == lines[i].line.length - 1)
                        paths[i] += "L" + x1 + "," + y1;
                    else
                        paths[i] += "L" + x1 + "," + y1 + "M" + x2 + "," + y2;
                } else {
                    if (j == 0)
                        paths[i] += "M" + lines[i].line[j][0] + "," + lines[i].line[j][1];
                    else
                        paths[i] += "L" + lines[i].line[j][0] + "," + lines[i].line[j][1];
                }
            }
        }

        $("#mySvg").empty();
        for (var i = 0; i < lines.length; i++) {
            var start = lines[i].line[0];
            var end = lines[i].line[lines[i].line.length - 1];
            if (squareDistance(start, end) == 0);
            if (squareDistance(start, end) < 1 && lines[i].diameter < 1) {
                var eraseCircle = false;
                for (var k = 0; k < eraserPointsIndex.length; k++) {
                    if (eraserPointsIndex[k].line == i) {
                        eraseCircle = true;
                        break;
                    }
                }
                if (!eraseCircle) {

                    svg.append("circle")
                        .attr("fill", "none")
                        .attr("stroke", strokeColor)
                        .attr("stroke-width", "1px")
                        .attr("r", "5px")
                        .attr("cx", (start[0] + lines[i].middle[0]) / 2 + "")
                        .attr("cy", (start[1] + lines[i].middle[1]) / 2 + "");
                }
            } else {
                svg.append("path")
                    .attr("d", paths[i])
                    .attr("stroke", strokeColor)
                    .attr("stroke-width", "2px")
                    .attr("fill", "none");
            }
        }
        var newContent = "";
        for (var i = 0; i < lines.length; i++) {
            if (i == 0)
                newContent += paths[i];
            else
                newContent += "\n" + paths[i];
        }
        pathContent =  pathContent+"\n"+newContent;
    }
});

//The Clear Button Function
$("#btnClear").click(function(evt) {
    c.clearRect(0, 0, canvas.width, canvas.height);
    $("#mySvg").empty();
    $("#pathD").val("");
    pathContent = "";
    lines = [];
    eraserPointsIndex = [];
});

//The Eraser Button Function
$("#btnEraser").click(function(evt) {
    isClear = true;
    $(canvas).css("cursor", "pointer");
});

//The Pen Button Function
$("#btnPen").click(function(evt) {
    isClear = false;
    $(canvas).css("cursor", "crosshair");
});

//The  colour-change Button Function
$("#btnColor").click(function(evt) {
    var x = document.getElementById("myColor");
    var defaultVal = x.defaultValue;
    var currentVal = x.value;
    strokeColor = currentVal;
});

$("#btnPost").click(function(evt) {
    var postContent = "";
    postContent = pathContent;
    sendInfo(postContent);
});

$("#btnSave").click(function(evt) {
    var type = 'jpg';
    downloadImage(type);
});

//To calculate the distance squared between the two points
function squareDistance(p1, p2) {
    return (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]);
}

//To judge if one point is in the eraser area
function isInEraser(point, mouse) {
    var a = Math.abs(point[0] - mouse[0]) <= eraserSize / 2.;
    var b = Math.abs(point[1] - mouse[1]) <= eraserSize / 2.;
    return a && b;
}

//To judge if one point locates in a certain circle
function isInCircle(point, center, radius) {
    return squareDistance(point, center) <= radius * radius
}

//To download Image
function downloadImage(type) {
    var imgdata = canvas.toDataURL(type);
    var fixtype = function(type) {
        type = type.toLocaleLowerCase().replace(/jpg/i, 'jpeg');
        var r = type.match(/svg|png|jpeg|bmp|gif/)[0];
        return 'image/' + r;
    }
    imgdata = imgdata.replace(fixtype(type), 'image/octet-stream')
    var saveFile = function(data, filename) {
        var link = document.createElement('a');
        link.href = data;
        link.download = filename;
        var event = document.createEvent('MouseEvents');
        event.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
        link.dispatchEvent(event);
    }
    var filename = new Date().toLocaleDateString() + '.' + type;
    saveFile(imgdata, filename);
}

//To send path content of the diagram and display responsed data
function sendInfo(pathData) {
    var msg = document.getElementById("pathD");
    var JSONObject = {
        "pathdata": pathData
    };
    var json = JSON.stringify(JSONObject);
    $.post("server.py", json, function(data, status) {
        printTikzCode(data);
    });
}

//To send path content of each stroke 
function sendStroke(strokeContent) {
    var JSONObject = {
        "strokedata": strokeContent
    };
    var json = JSON.stringify(JSONObject);
}

function printTikzCode(data) {
        var s = data
        var p = "\\[\\begin{tikzpicture}"
        s = data
        s = s.substring(1,s.length - 1);
        s = s.split("*")
        for (var i = 0; i < s.length - 1; i++) {
             p = p + '\n' + '  \\'+ s[i] ;
            }
        p = p +  '\n' + "\\[\\end{tikzpicture}"
        $("#pathD").val(p);
}