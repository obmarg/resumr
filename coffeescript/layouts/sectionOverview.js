(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define([], function() {
    var SectionOverview;
    return SectionOverview = (function(_super) {

      __extends(SectionOverview, _super);

      function SectionOverview() {
        SectionOverview.__super__.constructor.apply(this, arguments);
      }

      SectionOverview.prototype.template = '#section-overview-template';

      SectionOverview.prototype.regions = {
        sidebar: '#sidebar',
        content: '#content'
      };

      return SectionOverview;

    })(Backbone.Marionette.Layout);
  });

}).call(this);
