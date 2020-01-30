//グローバル変数
var items = [];
var tUrl = 'http://localhost:8081/';
var all = 'all';
var sflag = 0;
var savedata;

function today() {
  var d = new Date();
  var formatted = `${d.getFullYear()}-${(d.getMonth()+1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
  return formatted;
}

function scraping() {  
  $(function(){
    var targetUrl = tUrl+'scraping';
      $.ajax({
          url: targetUrl,
          type: 'POST',
          scriptCharset: 'utf-8',
      }).done(function(data){ 
          $('#table').empty();
          $('#iimg').empty();
          if (data == 'True') {
            $('#table').append('<tr><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">INFO</div></td><td><div style="font-style: italic;color: #FFFF00;font-size:xx-large ;font-weight: 700;">FINISH</div></td></tr>');
            var pastDate = null; 
            other(all,pastDate);
          } else {
            $('#table').append('<tr><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">INFO</div></td><td><div style="font-style: italic;color: #FF3300;font-size:xx-large ;font-weight: 700;">FAILURE</div></td></tr>');
          }
          sflag = 0;
          getPastDay();
        }).fail(function(data, XMLHttpRequest, textStatus) {
          console.log(data);
          $('#table').empty();
          $('#iimg').empty();
          $('#table').append('<tr><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">INFO</div></td><td><div style="font-style: italic;color: #FF3300;font-size:xx-large ;font-weight: 700;">FAILURE</div></td></tr>');
          alert('通信失敗');
          sflag = 0;
          console.log("XMLHttpRequest : " + XMLHttpRequest.status);
          console.log("textStatus     : " + textStatus);
      });
  });
}

function other(other,pastDate) {

  var targetUrl = tUrl+'other';
  var date = null;

  if (pastDate == null || pastDate == '') {
    date = today();  
  } else {
    date = pastDate;
  }

  if (date != null) {
    if (other == all) {
      var request = {
          'date' : date,
          'other': all
      };
    } 
  } else {
    alert('不正な日付');
    var request = {
      'date' : today(),
      'other': all
    };
  }

  $(function() {
      $.ajax({
          url: targetUrl,
          type: 'POST',
          contentType: 'application/JSON',
          dataType: 'JSON',
          data : JSON.stringify(request),
          scriptCharset: 'utf-8',
      }).done(function(data) { 
          if (data == null || data == '' || data[0] == '') {
            $('#table').empty();
            $('#iimg').empty();
            $('#table').append('<tr><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">INFO</div></td><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">NO DATA</div></td></tr>');
          } else {
            show(data);
            savedata = data;
          }
        }).fail(function(data, XMLHttpRequest, textStatus) {
          alert('通信失敗');
          window.location.reload();
          console.log(data);
          console.log("XMLHttpRequest : " + XMLHttpRequest.status);
          console.log("textStatus     : " + textStatus);
      });
  });
}

function getPastDay() {  
  $(function(){
    var targetUrl = tUrl+'getPastDay';    
      $.ajax({
          url: targetUrl,
          type: 'POST',
          contentType: 'application/JSON',
          dataType: 'JSON',
          data : null,
          scriptCharset: 'utf-8',
      }).done(function(data) { 
          if (data == null || data == '' || data[0] == '') {
            $('#table').empty();
            $('#iimg').empty();
            $('#table').append('<tr><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">INFO</div></td><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">NO DATA</div></td></tr>');
          } else {
            $('#ddmenu').empty(); 
            $("#ddmenu").append('<option value="">PAST DATA</option>');
            for (var i = 0; i < data.length; i++) {
              //console.log(data);
              $("#ddmenu").append('<option value="'+data[i].dt+'"style="font-weight: 600;" >'+data[i].dt+'</option>');
            }
          }
        }).fail(function(data, XMLHttpRequest, textStatus) {
          alert('通信失敗');
          window.location.reload();
          console.log(data);
          console.log("XMLHttpRequest : " + XMLHttpRequest.status);
          console.log("textStatus     : " + textStatus);
      });
  });
}
////////////////////////////////////////////////////////////////////////////////////////////////
//CSV download
//jsonをcsv文字列に編集する
function jsonToCsv(json, delimiter) {
  var header = Object.keys(json[0]).join(delimiter) + "\n";
  var body = json.map(function(d){
      return Object.keys(d).map(function(key) {
          return d[key];
      }).join(delimiter);
  }).join("\n");
  return header + body;
}

//csv変換
function exportCSV(items, delimiter, filename) {

  //文字列に変換する
  var csv = jsonToCsv(items, delimiter);

  //拡張子
  var extention = delimiter==","?"csv":"tsv";

  //出力ファイル名
  var exportedFilenmae = (filename  || 'export') + '.' + extention;
  //文字化け対策
  var bom = new Uint8Array([0xEF, 0xBB, 0xBF]);

  //BLOBに変換
  var blob = new Blob([bom,csv], { type: 'text/csv;charset=utf-8;' });

  if (navigator.msSaveBlob) { // for IE 10+
      navigator.msSaveBlob(blob, exportedFilenmae);
  } else {
      //anchorを生成してclickイベントを呼び出す。
      var link = document.createElement("a");
      if (link.download !== undefined) {
          var url = URL.createObjectURL(blob);
          link.setAttribute("href", url);
          link.setAttribute("download", exportedFilenmae);
          link.style.visibility = 'hidden';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      }
  }
}


function output(){
    console.log(savedata);
    if (savedata == null || savedata == 0) {
      alert("No data");
    } else {
      var filename = savedata[0].dt;;
      exportCSV(savedata,',', filename);
    }
    
}
////////////////////////////////////////////////////////////////////////////////////////////////
window.onload = function() {
  //today
  var pastDate = null; 
  other(all,pastDate);
  getPastDay();
}

//scraping
$(function(){ 
  $('#start').on('click',function(){
    if (sflag == 0) {
      sflag = 1;
      scraping();
      $('#table').empty();
      $('#iimg').empty();
      $('#table').append('<tr><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">INFO</td><td><div style="font-style: italic;color: #0000FF;font-size:xx-large ;font-weight: 700;">RUNNING　<img src="./static/img/ico/load.gif" width="30" height="30" /></div></td></tr>');
    } else {
      $('#table').empty();
      $('#iimg').empty();
      $('#table').append('<tr><td><div style="font-style: italic;color: #000000;font-size:xx-large ;font-weight: 700;">INFO</td><td><div style="font-style: italic;color: #0000FF;font-size:xx-large ;font-weight: 700;">RUNNING NOW ( PLEASE WAIT A MINUTE )　<img src="./static/img/ico/load.gif" width="30" height="30" /></div></td></tr>');
    }  
  });
});

//TODAY
$(function() {
  $('.other').on('click',function() {
    var id = $(this).attr('id');
    var pastDate = null;
    if (id == all) {
      other(all,pastDate);
    } 
  });
});

//プルダウン選択時
$(function() {
  $('#ddmenu').on('click',function() {
    var pastDate = $("#ddmenu").val();
    other(all,pastDate);
  });
});

//$(function() {
//  $('.reset').on('click',function() {
//    window.location.reload();
//  });
//});

function show(data) {
  $(function() {
    
    $('#table').empty();
    $('#iimg').empty();
    for (var i = 0; i < data.length; i++) {
      
    console.log(data[i].dt);
    var dirDay = data[i].dt;
    var dirNaeme = dirDay.replace( /-/g , "" );
    dirNaeme = dirNaeme.substr(0,8);

    console.log(dirNaeme);

      var id = i+1;
      $('#table').append('<tr><td><a href='+data[i].url+'target="_blank" style="font-size: x-large;">'+data[i].title+'</a></br>('+data[i].dt+')</td><td><a href='+data[i].url+' target="_blank"><img src="./static/img/Selenium/'+dirNaeme+'/'+data[i].img_id+'.png" width="600" height="450" alt=""></a></td></tr>');
    }  
  });
  return data;
}




