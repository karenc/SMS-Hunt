function ListEdit(clues, elementId, headers, fields) {
    this.element = jQuery('#' + elementId);
    this.fields = fields;

    var tr = jQuery('<tr></tr>').appendTo(this.element);
    var i;
    for (i = 0; i < headers.length; i++) {
        var th = jQuery('<th></th>').appendTo(tr);
        th.text(headers[i]);
    }
    jQuery('<th>Delete</th>').appendTo(tr);

    this.render(clues);
}

ListEdit.prototype.addEventHandler = function(handler) {
    var this_ = this;
    function inner(e) {
        this_[handler](e, this);
    }
    return inner;
}

ListEdit.prototype.renderClue = function(clue, action) {
    var tr = jQuery('<tr></tr>');
    var i;
	var input;

    for (i = 0; i < this.fields.length; i++) {
        input = jQuery('<input type="text" />').val(clue[this.fields[i]]).appendTo(jQuery('<td></td>').appendTo(tr));
		input.attr('name', this.fields[i]);
    }

    var button = jQuery('<input type="button" />').appendTo(jQuery('<td></td>').appendTo(tr));
    button.attr('class', action);
    button.val(action);

    return tr;
};

ListEdit.prototype.render = function(clues) {
    var i;

    for (i = 0; i < clues.length; i++) {
        this.element.append(this.renderClue(clues[i], 'Delete'));
    }
	jQuery('.Delete').click(this.addEventHandler('deleteClue'));

    this.element.append(this.renderClue({}, 'Create'));
    jQuery('.Create').click(this.addEventHandler('createClue'));
};

ListEdit.prototype.createClue = function(e, element) {
	var tr = jQuery(element).parent().parent();
	var i;
	var clue = {};
	var input;
	for (i = 0; i < this.fields.length; i++) {
		input = tr.find('input[name=' + this.fields[i] + ']');
		clue[this.fields[i]] = input.val();
		input.val('');
	}
	this.element.find('tr:last').before(this.renderClue(clue, 'Delete'));
	jQuery('.Delete').click(this.addEventHandler('deleteClue'));
}

ListEdit.prototype.deleteClue = function(e, element) {
    var tr = jQuery(element).parent().parent();
    tr.remove();
}
