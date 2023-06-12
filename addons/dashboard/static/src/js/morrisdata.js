$(function() {
	$(document).on('click', "#refresh", function () {
		  location.reload();
	  });
	$.getJSON('/page/dashboard', {}, function(result) {
		
		$('.oe_kanban_record').css( "min-width", "100%" );
		$.each(result, function(index, value) {
			var data_result = [];
			$.each(value[1], function(i, valeur) {
				if (valeur.date) {
					var val = {
							period: valeur.date,
							mesure :valeur.mesure
					};
					data_result.push(val);
				}

			});
			MorisIndex = value[0];

			if (value[2]==1){
				Morris.Area({
					element : 'morris-area-chart' + MorisIndex.toString(),
	
					data : data_result,
					xkey : 'period',
					ykeys : ['mesure'],
					labels : ['Mesure'],
					pointSize : 2,
					hideHover : 'auto',
					resize : true
	
				});
			}
			if (value[2]==2){
				
				Morris.Bar({
					element : 'morris-bar-chart' + MorisIndex.toString(),
					data : data_result,
					xkey : 'period',
					ykeys : ['mesure'],
					labels : ['Mesure'],
					barRatio : 0.4,
					xLabelAngle : 35,
					hideHover : 'auto',
					resize : true
				});

			}
		});
		
	});
});