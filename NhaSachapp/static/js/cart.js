function addToCart(id,name,price){


    event.preventDefault()


    fetch('/api/add-cart',{
        method : 'post',
        body: JSON.stringify ({
            'id': id,
            'name': name,
            'price': price
        }),

        headers:{
            'Content-Type':'application/json'
        }
    }).then(function(res){
        console.info(res)
        return res.json()
    }).then(function(data){
        console.info(data)

        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity
    }).catch(function(err){
        console.error(err)
    })
}


function pay(){
    if (confirm('Bạn chắc chắn thanh toán ?') == true){

            fetch('/api/pay', {
            method : 'post',

        }).then(function(res){

            return res.json()
        }).then(function(data){

            if(data.code == 200)
                location.reload()
        }).catch(function(err){
            console.error(err)
        })
    }
}


function updateCart(id, obj) {
    fetch('/api/update-cart', {
        method: 'put',
        body: JSON.stringify({
            'id': id,
            'quantity': parseInt(obj.value)
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity

        let amount = document.getElementById('total-amount')
        amount.innerText = new Intl.NumberFormat().format(data.total_amount)
    })
}


function deleteCart(id) {
    if (confirm("Ban chac chan xoa san pham nay khong?") == true) {
        fetch('/api/delete-cart/' + id, {
        method: 'delete',
        headers: {
            'Content-Type': 'application/json'
        }
        }).then(res => res.json()).then(data => {
        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity

        let amount = document.getElementById('total-amount')
        amount.innerText = new Intl.NumberFormat().format(data.total_amount)

        let e = document.getElementById("product" + id)
        e.style.display = "none"
        }).catch(err => console.error(err))
    }
}


function addComment(productId) {
    let content = document.getElementById('commentContent')
    if (content != null) {
        fetch('/api/comments', {
            method: 'post',
            body: JSON.stringify({
                'content': content.value,
                'product_id': productId
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            console.info(data)
            if (data.status == 200) {
                let comments = document.getElementById('comments')
                comments.innerHTML = getHtmlComment(data.comment) + comments.innerHTML
                content.value = ""
            } else
                alert("Thêm bình luận thất bại!!!")
        }).catch(err => console.error(err))
    }
}


function getHtmlComment(comment) {
    let image = comment.user.avatar
    if (image === null || !image.startsWith('https'))
        image = '/static/images/book.jpg'

    return `
        <div class="row">
            <div class="col-md-1 col-xs-4">
                <img src="${image}"
                class="img-fluid rounded-circle" alt="${comment.user.username}" >
            </div>
            <div class="col-md-11 col-xs-8">
                <p>${comment.content}</p>
                <p><em>${moment(comment.created_date).fromNow() }</em></p>
            </div>
        </div>`
}


function loadComments(productId, page=1) {
    fetch(`/api/products/${productId}/comments?page=${page}`).then(res => res.json()).then(data => {
        console.info(data)
        let comments = document.getElementById('comments')
        comments.innerHTML = ""
        for (let i = 0; i < data.length; i++)
            comments.innerHTML += getHtmlComment(data[i])
    })
}


function addUserInfo(){
    if (confirm('Bạn chắc chắn thanh toán ?') == true){
            fetch('/pay_receipt', {
            method: 'post',
//            body: JSON.stringify({
//                'phonenum': phoneNum),
//                  'address': address),
//                  'paymethod': payMethod)
//            }),
//            headers: {
//                'Content-Type': 'application/json'
//            }
        }).then(function(res){
            return res.json()
        }).then(function(data){
            if(data.code == 200)
                location.reload()
        }).catch(function(err){
            console.error(err)
        })
    }
}


//PayReceipt//
function openCity(cityName, elmnt, color) {
  // Hide all elements with class="tabcontent" by default */
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Remove the background color of all tablinks/buttons
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].style.backgroundColor = "";
  }

  // Show the specific tab content
  document.getElementById(cityName).style.display = "block";

  // Add the specific color to the button used to open the tab content
  elmnt.style.backgroundColor = color;
}
