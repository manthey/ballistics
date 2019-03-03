<template>
  <div id="mainpage">
    <vue-markdown>
# Ballistics of Historical Black Powder Tests

This attempts to answer the question of how black powder has varied over time.  The main technique is to gather historical test data and use modern external ballistics to calculate the usefully generated power per unit weight of the gunpowder used in each test.

The main focus is on the 18th century.  One question in particular is how the black powder we purchase today compares with the powder that was produced commercially in the 18th century.

The scope of this research is focused on black powder as a relatively mature technology when it was when it was a ubiquitous and required substance.

## Gunpowder

Gunpowder was a critical necessity in warfare, hunting, and mining.  There are numerous histories on the early developments of gunpowder and on its ultimate decline and replacement.  Despite this, there has not been a general history of gunpowder in the age of scientific sieges and lineal field battles.  This oversight is, at least in part, due to the perceived lack of substantial technological development of gunpowder.

Gunpowder in the 17th through 19th centuries was a manufactured commodity.  The users of gunpowder generally did not need to know the specifics of how it was made.  As there were virtually no alternatives to gunpowder, there was little need to know how it compared to other substances.  This prevented much general curiosity about gunpowder, which, in turn, limited the number of scientists and engineers who worked to improve the product.

Despite this, gunpowder manufacturing evolved significantly.  Not all of the changes made a better product, as many innovations were for safety or cost reduction.  Similarly, what constitutes improved gunpowder depends on the goals -- some changes were to improve the strength of the powder, while others were done to improve the life-span of the substance.

At the end of the 18th century, chemistry was undergoing a revolution, and the scientific method was being more widely used.  Gunpowder was examined anew, resulting in many publications and several attempts at improvement.  Some of these improvements resulted in inflated, preposterous claims, while others were quite useful.  Although the tools for quantifying these improvements existed, they would not be fully employed until the middle of the 19th century.

Most histories of gunpowder begin with its original discovery and origin.  There are different opinions about the first country to use gunpowder.  It is not a new observation, but in order to determine where and when gunpowder was invented, the exact substance that constitutes gunpowder must be specified.  It can be claimed that gunpowder is any substance that deflagrates and contains a nitrate.  At the other extreme, gunpowder is a specific ratio of saltpeter, charcoal, and sulfur, intimately ground so as to have some minimum combustion speed, and formed into grains.  Possibly the most sensible definition of gunpowder would be that it is any powdered composition that can be used to fire a projectile from a gun.

For purposes of this study, gunpowder is the commercial product made from saltpeter, sulfur, charcoal, and minor other components, as sold to and used by the military and civilians for artillery, small arms, and mining.  The early history of gunpowder is not covered.  Furthermore, this study is biased towards English and French gunpowder, with some additional information on the manufacture of gunpowder by other European nations and in America.

Today gunpowder is more commonly referred to as black powder.  This distinction is made to separate the original gunpowder from newer propellants used to fire guns.  The term gunpowder will be used to always mean black powder and its direct variations.

Gunpowder was the only commercial explosive of any significance until the mid 19th century.  As such, it was called on to fill a number of uses.  The three principal uses were military service, sporting, and blasting.  Military service used gunpowder for ordnance, for small arms, for grenades and other specialty weapons, and for mines.  Sporting comprised recreational and subsistence hunting as well as target shooting.  Blasting included civil engineering and both open pit mining and deep shaft mining.

Depending on the principal use of gunpowder, different properties are desirable.  For service powder, the greatest possible strength is sought, thus minimizing the amount of materiel that requires transport.  For sporting powder, the most certain and quick inflammation is requisite, to minimize the delay between pulling the trigger and the gun firing at the target.  For blasting powder, the greatest quantity of expanding gas is desired, to maximize the shock to the surrounding rocks and earth. [Berthelot, 1892, p. 477](references?refkey=berthelot1892)

It is also desirable for most gunpowder to also be resistant to moisture.  The powder should have a minimum of degradation due to age and transportation.  Lastly, the gunpowder needs to be inexpensive for the customer, yet profitable for the manufacturer.

Since there are different goals for different uses of gunpowder, manufacturers usually produced multiple types of powder.  Besides the basic composition of the powder, the granulation size was varied to better match specific uses of the gunpowder.  In addition to the three main applications of gunpowder listed above, specialty powder was made for fireworks and for certain foreign trade.  Multiply qualities of gunpowder were also manufactured and sold to accommodate different budgets.

Today, most uses of gunpowder have been superceded by modern explosives, though gunpowder still has applications for military service, sporting, and blasting.  Gunpowder manufacturers still produce multiple grades, granulations, and qualities of gunpowder.

## Data Sources

In an effort to characterize the quality of gunpowder over time, a variety of historical sources have been used.  Any source where there is an experiment with enough information to calculate the realized power per weight of gunpowder could be used.  This includes range tests, calorimeter measurements, velocities measured with ballistic pendulums and chronometers, trajectory tracks, time of flight, and other methods.  Some proof standards and textbook problems have also been used, though these are of limited value.

Currently, ballistics calculations are limited to spherical projectiles, as drag models for other shapes are substantially more complicated.  Where available, information such as temperature, pressure, and humidity are used to refine computations.  Ideally, one would use the smoothness and sphericity of the projectile as well, but this is essentially never recorded.

There are certainly more sources than have been used; please forward references when possible.
    </vue-markdown>
  </div>
</template>

<style scoped>
#mainpage {
  padding: 10px;
  max-width: 1000px;
  margin: 0 auto;
}
</style>

<script>
export default {
  name: 'MainPage'
}
</script>
