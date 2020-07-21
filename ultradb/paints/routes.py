from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, jsonify
from ultradb.paints.forms import PaintColorBuilderForm, NewSupplierForm, NewBrandForm, NewProductForm, NewColorForm
from ultradb.models import Area, Supplier, Brand, Product, Sheen, Paint, Color, PaintColor
from ultradb import db


paint_bp = Blueprint('paint_bp', __name__)


# Add a new Supplier
@paint_bp.route("/newsupplier", methods=['GET', 'POST'])
def add_supplier():
    form=NewSupplierForm()
    if form.validate_on_submit():
        newSupplier = Supplier(name=form.name.data, addr_str=form.addr_str.data, city=form.city.data)
        db.session.add(newSupplier)
        db.session.commit()
        flash('New Supplier Added Successfully!', 'success')
        return redirect(url_for('paint_bp.paint_builder'))
    return render_template('add_supplier.html', title='Add a New Supplier', legend='Add a New Supplier', form=form)

# Add a new Brand
@paint_bp.route("/newbrand", methods=['GET', 'POST'])
def add_brand():
    form=NewBrandForm()
    form.supplier.query = Supplier.query
    if form.validate_on_submit():
        newBrand = Brand(name=form.name.data, supplier_id=form.supplier.data.id)
        db.session.add(newBrand)
        db.session.commit()
        # Add brand to supplier?

        flash('New Brand Added Successfully!', 'success')
        return redirect(url_for('paint_bp.paint_builder'))
    if request.method == 'GET':
        form.supplier.data = Supplier.query.first()
    return render_template('add_brand.html', title='Add a New Brand', legend='Add a New Brand', form=form)

# Add a new Product
@paint_bp.route("/newproduct", methods=['GET', 'POST'])
def add_product():
    form=NewProductForm()
    form.brand.query = Brand.query
    if form.validate_on_submit():
        newProduct = Product(name=form.name.data, brand_id=form.brand.data.id)
        db.session.add(newProduct)
        db.session.commit()
        flash('New Product Added Successfully!', 'success')
        return redirect(url_for('paint_bp.paint_builder'))
    if request.method == 'GET':
        form.brand.data = Brand.query.first()
    return render_template('add_product.html', title='Add a New Product', legend='Add a New Product', form=form)

# Add a new Color
@paint_bp.route("/newcolor", methods=['GET', 'POST'])
def add_color():
    form=NewColorForm()
    if form.validate_on_submit():
        newColor = Color(name=form.name.data, code=form.code.data)
        db.session.add(newColor)
        db.session.commit()
        flash('New Color Added Successfully!', 'success')
        return redirect(url_for('paint_bp.paint_builder'))
    return render_template('add_color.html', title='Add a New Color', legend='Add a New Color', form=form)


# Create a new PaintColor
@paint_bp.route("/paintBuilder", methods=['GET', 'POST'])
def paint_builder():
    form = PaintColorBuilderForm()
    form.supplier.query = Supplier.query
    form.brand.query = Brand.query
    form.product.query = Product.query
    form.sheen.query = Sheen.query
    form.color.query = Color.query
    if form.validate_on_submit():
        # Add Paint to db
        paint = Paint(supplier_id= form.supplier.data.id, 
                      brand_id= form.brand.data.id, 
                      product_id= form.product.data.id, 
                      sheen_id= form.sheen.data.id)
        db.session.add(paint)
        db.session.commit()
        # Add PaintColor to db
        paintcolor = PaintColor(paint_id=paint.id, 
                                color_id=form.color.data.id,
                                prod_code= form.prod_code.data,
                                base= form.base.data,
                                formula= form.formula.data)
        db.session.add(paintcolor)
        db.session.commit()
        flash('New PaintColor Added Successfully!', 'success')
        return redirect(url_for('main_bp.home'))
    if request.method=='GET':
        # Set the intial values for the dropdown boxes
        form.supplier.data = ' '
        # # limit the Brands and Products to those of the selected supplier.
        # # This is best (only) done with AJAX or JQuery
        # form.brand.data = Brand.query.first()
        # form.product.data = Product.query.first()
        # form.sheen.data = Sheen.query.first()
        # form.color.data = Color.query.first()
    return render_template('paint_builder.html', title='Create a New PaintColor', legend='Create a New PaintColor', form=form)

#########################################################
###################### JSON Routes ######################
#########################################################
@paint_bp.route("/getbrands/<supplier>")
def brand(supplier):
    # Get all brands for the given supplier
    brands = Brand.query.filter_by(supplier_id=supplier).all()
    # Create an empty list
    brandArray = []
    # go through returned brands and append as obj to list
    for brand in brands:
        brandObj = {}
        brandObj['id'] = brand.id 
        brandObj['name'] = brand.name  
        brandArray.append(brandObj)
    # Return 'brands' of given supplier as json data
    return jsonify({'brands' : brandArray})

@paint_bp.route("/getproducts/<brand>")
def product(brand):
    # Get all products for the given brand
    products = Product.query.filter_by(brand_id=brand).all()
    # Create an empty list
    productArray = []
    # go through returned products and append as obj to list
    for product in products:
        productObj = {}
        productObj['id'] = product.id 
        productObj['name'] = product.name  
        productArray.append(productObj)
    # Return 'products' of given brand as json data
    return jsonify({'products' : productArray})

@paint_bp.route("/getareas/<site>")
def area(site):
    # Get all areas for the given site
    areas = Area.query.filter_by(site_id=site).all()
    # Create an empty list
    areaArray = []
    # go through returned products and append as obj to list
    for area in areas:
        areaObj = {}
        areaObj['id'] = area.id 
        areaObj['name'] = area.name  
        areaArray.append(areaObj)
    # Return 'products' of given brand as json data
    return jsonify({'areas' : areaArray})
