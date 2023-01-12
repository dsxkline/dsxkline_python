dsxkline_html = r"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content = "width=device-width,height=device-height,initial-scale=1.0,user-scalable=no">
    <title>大师兄K线图</title>
    <style>*{padding:0;margin:0;-webkit-touch-callout:none;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;}html{overflow:hidden;}body{position:fixed;top:0;left:0;overflow:hidden;width:100%;height:100%;}</style>
    <script id="klinejs">{jscontent}</script>
    <style type="text/css">
      body{
        background-color: -background-color-;
      }
    </style>
  </head>
  <body>
       <div id="kline" style="display: block;"></div>
  </body>
</html>
<script>
</script>
"""