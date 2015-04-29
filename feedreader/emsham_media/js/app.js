var feedobj = $('#feed-ul');

var Item = Backbone.Model.extend({
    urlRoot: '/pin/api/post/?format=json&thumb_size=192'
});
var Posts = Backbone.Collection.extend({
    url: '/pin/api/post/?format=json&thumb_size=192',
    model: Item,
    initialize: function(){
      this.fetch();
    }
});

//var instance = new Posts();
//instance.fetch(); //fetches at /some/path

var ItemView = Backbone.View.extend({
    tagName: 'div', // name of tag to be created
    className: 'feed-item',
    
    // `initialize()` now binds model change/removal to the corresponding handlers below.
    initialize: function(){
      _.bindAll(this, 'render', 'unrender', 'remove'); // every function that uses 'this' as the current object should be in here
      this.afterRender(); 
    },
    // `render()` now includes two extra `span`s corresponding to the actions swap and delete.
    render: function(){
      var variables = {
        'thumbnail': this.model.get('thumbnail'),
        'id': this.model.get('id'),
        'permalink': this.model.get('permalink'),
        'text': this.model.get('text'),
        'user_avatar': this.model.get('user_avatar'),
        'user_name': this.model.get('user_name'),
        'hw': this.model.get('hw').split('x'),

      }
      var template = _.template( $("#feed-item-template").html(), variables );
      $(this.el).html(template);
      //feedobj.masonry('reload');

      return this; // for chainable calls, like .render().el
    },
    afterRender: function() { 
      //alert('after');
      console.log('afterRender'); 
      feedobj.masonry('reload');
    } ,
    // `unrender()`: Makes Model remove itself from the DOM.
    unrender: function(){
      $(this.el).remove();
    },
    
    // `remove()`: We use the method `destroy()` to remove a model from its collection. Normally this would also delete the record from its persistent storage, but we have overridden that (see above).
    remove: function(){
      this.model.destroy();
    }
  });

// Because the new features (swap and delete) are intrinsic to each `Item`, there is no need to modify `ListView`.
var ListView = Backbone.View.extend({
    el: $('#feed-ul'), // el attaches to existing element
    mason : false,
    events: {
      'click button#add': 'addItem'
    },
    initialize: function(){
      _.bindAll(this, 'render', 'addItem', 'appendItem'); // every function that uses 'this' as the current object should be in here

      this.collection = new Posts;
      this.collection.bind('add', this.appendItem); // collection event binder

      this.counter = 0;
      this.render();
      this.afterRender(); 
    },
    render: function(){
      var self = this;
      //$(this.el).append("<button id='add'>Add list item</button>");
      //$(this.el).append("<ul></ul>");
      _(this.collection.models).each(function(item){ // in case collection is not empty
        self.appendItem(item);
      }, this);
      
    },
    afterRender: function() { 
      
      $(this.el).masonry({
          itemSelector : '.feed-item',
          isRTL: true,
          isAnimated: false,
          isFitWidth: true,
      });
      feedobj.masonry('reload');
    }, 
    addItem: function(){
      this.counter++;
      var item = new Item();
      item.set({
        part2: item.get('part2') + this.counter // modify item defaults
      });
      this.collection.add(item);
    },
    appendItem: function(item){
      var itemView = new ItemView({
        model: item
      });
      $(this.el).append(itemView.render().el);
    }
  });



$(document).ready(function(){
  var listView = new ListView();  
});