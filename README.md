## flask框架

### 路由

#### 简单路由

```python
@app.route("/view")
def say_view():
    return "view,you are good!"
```

#### 带参数的路由

```python
@app.route("/show/<int:id>")
def show_id(id):
    return str(id);
```

<iframe 
    height=450 
    width=800 
    src='http://player.youku.com/embed/XMzMxMjE0MjY4NA==' 
    frameborder=0 
    'allowfullscreen'>
</iframe>

