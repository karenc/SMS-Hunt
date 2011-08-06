function ListEdit(values, elementId, headers, fields) {
    this.element = jQuery('#' + elementId);
    this.fields = fields;
    this.hidden = jQuery('input[name=' + elementId + ']');

    var tr = jQuery('<tr></tr>').appendTo(this.element);
    var i;
    for (i = 0; i < headers.length; i++) {
        var th = jQuery('<th></th>').appendTo(tr);
        th.text(headers[i]);
    }
    jQuery('<th>Delete</th>').appendTo(tr);

    this.render(values);

    jQuery('#' + elementId + '-save').click(this.addEventHandler('save'));
}

ListEdit.prototype.addEventHandler = function(handler) {
    var this_ = this;
    function inner(e) {
        this_[handler](e, this);
    }
    return inner;
}

ListEdit.prototype.renderValue = function(value, action) {
    var tr = jQuery('<tr></tr>');
    var i;
    var input;

    for (i = 0; i < this.fields.length; i++) {
        input = jQuery('<input type="text" />').val(value[this.fields[i]]).appendTo(jQuery('<td></td>').appendTo(tr));
        input.attr('name', this.fields[i]);
    }

    var button = jQuery('<input type="button" />').appendTo(jQuery('<td></td>').appendTo(tr));
    button.attr('class', action);
    button.val(action);

    return tr;
};

ListEdit.prototype.render = function(values) {
    var i;

    for (i = 0; i < values.length; i++) {
        this.element.append(this.renderValue(values[i], 'Delete'));
    }
    jQuery('.Delete').click(this.addEventHandler('deleteValue'));

    this.element.append(this.renderValue({}, 'Create'));
    jQuery('.Create').click(this.addEventHandler('createValue'));
};

ListEdit.prototype.createValue = function(e, element) {
    var tr = jQuery(element).parent().parent();
    var i;
    var value = {};
    var input;
    for (i = 0; i < this.fields.length; i++) {
        input = tr.find('input[name=' + this.fields[i] + ']');
        value[this.fields[i]] = input.val();
        input.val('');
    }
    this.element.find('tr:last').before(this.renderValue(value, 'Delete'));
    jQuery('.Delete').click(this.addEventHandler('deleteValue'));
}

ListEdit.prototype.deleteValue = function(e, element) {
    var tr = jQuery(element).parent().parent();
    tr.remove();
}

ListEdit.prototype.save = function(e, element) {
    e.preventDefault();
    var i;
    var j;
    var trs = this.element.find('tr');
    var results = [];
    var obj;
    var inputs;
    var input;

    for (i = 0; i < trs.length; i++) {
        obj = {};
        inputs = jQuery(trs[i]).find('input');
        for (j = 0; j < inputs.length; j++) {
            input = jQuery(inputs[j]);
            if ((this.fields.indexOf(input.attr('name')) !== -1) && input.val()) {
                obj[input.attr('name')] = input.val();
            }
        }
        if (!jQuery.isEmptyObject(obj)) {
            results.push(obj);
        }
    }
    this.hidden.val(jQuery.toJSON(results));
    this.element.parent().submit();
}
