console.log("working fine");


const monthName =  ["Jan","Feb","Mar","April","May","June",
                   "July","Aug","Sept","Oct","Nov","Dec",]

                   
// const dayName = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat",]



$("#commentForm").submit(function(e){
    e.preventDefault();
    let day = new Date("October 31, 2021 09:38:00").getDate();
    let dt = new Date();
    let time = dt.getUTCDate() + " " + monthName[dt.getUTCMonth()] + ", " + dt.getFullYear()

    $.ajax({
        data: $(this).serialize(),

        method: $(this).attr("method"),

        url: $(this).attr("action"),

        dataType: "json",

        success: function(res){
            console.log("comment saved to db...");


            if(res.bool == true){
                $("#review-res").html("Review added successfully.. ")
                $(".hide-comment-form").hide()
                $(".add-review").hide()

                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                    _html += '<div class="user justify-content-between d-flex">'
                    _html += '<div class="thumb text-center">'
                    _html += '<img src="https://i0.wp.com/rssoeroto.ngawikab.go.id/wp-content/uploads/2022/07/user-dummy-removebg.png?ssl=1" alt="" />'
                    _html += '<a href="#" class="font-heading text-brand">'+ res.context.user +'</a>'
                    _html += '</div>'

                    _html += '<div class="desc">'
                    _html += '<div class="d-flex justify-content-between mb-10">'
                    _html += '<div class="d-flex align-items-center">'
                    _html += '<span class="font-xs text-muted">'+ time +'</span>'
                    _html += '</div>'

                    for(let i = 1; i <= res.context.rating; i++){
                        _html += '<i class="ri-star-fill text-warning"></i>'
                    }

                    _html += '</div>'
                    _html += '<p class="mb-10">'+ res.context.review +'</p>'
                    _html += '</div>'
                    _html += '</div>'
                    _html += '</div>'

                    $(".comment-list").prepend(_html)
            }
            

        }
    })
})


$(document).ready(function (){
    $(".filter-checkbox,#price-filter").on("click", function(){
        console.log("checkbox have been clicked");

        let filter_object = {}

        let min_price = $("#max_price").attr("min")
        let max_price = $("#max_price").val()

        filter_object.min_price = min_price;
        filter_object.max_price = max_price;

        $(".filter-checkbox").each(function(){
            let filter_value = $(this).val()
            let filter_key = $(this).data("filter")

            // console.log("filter value is :", filter_value);
            // console.log("filter key is :", filter_key);

            filter_object[filter_key] = Array.from(document.querySelectorAll('input[data-filter=' + filter_key + ']:checked')).map(function(element){
                return element.value
            })
        })
        console.log("Filter object is",filter_object);

        $.ajax({
            url: '/filter-products',
            data: filter_object,
            dataType: 'json',
            beforeSend: function(){
                console.log("trying to filter product...");

            },
            success: function(res){
                console.log(res);
                console.log("data filtred successfully");
                $("#filtered-product").html(res.data)
            }
        })       
    })
    
    $("#max_price").on("blur", function(){
        var min_price = $(this).attr("min")
        var max_price = $(this).attr("max")
        var current_price = $(this).val()
        
        // console.log("Current price is:",current_price);
        // console.log("Max price is:",max_price);
        // console.log("Min price is:",min_price);

        if(current_price < parseInt(min_price) || current_price > parseInt(max_price)){
            // console.log("error")

            alert("Price must between $" +min_price + 'and $' + max_price)
            $(this).val(min_price)
            $("#range").val(min_price)
        }


    })

})



// Add to cart functionality

$("#add-to-cart-btn").on("click", function(){
    let quantity  = $("#product-quantity").val()
    let product_title = $(".product-title").val()
    let product_id = $(".product-id").val()
    let current_price = $("#current_price").text()
    let this_val = $(this)

    console.log("Quantity:",quantity);
    console.log("Title:",product_title);
    console.log("ID:",product_id);
    console.log("Quantity:",quantity);
    console.log("Price:",current_price);
    console.log("Current element:",this_val);

    $.ajax({
        url: '/add-to-cart',
        data: {
            'id': product_id,
            'qty': quantity,
            'title': product_title,
            'price': current_price,
        },
        dataType: 'json',
        beforeSend: function(){
            console.log("Adding product to cart");
        },
        success: function(res){
            this_val.html("Item added to cart")
            console.log("Added product to cart");
            $(".cart-items-count").text(res.totalcartitems)
        }
    })

})